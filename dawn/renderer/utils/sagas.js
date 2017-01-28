/**
 * Redux sagas are how we handle complicated asynchronous stuff with redux.
 * See http://yelouafi.github.io/redux-saga/index.html for docs.
 * Sagas use ES6 generator functions, which have the '*' in their declaration.
 */

import fs from 'fs';
import _ from 'lodash';
import { delay, eventChannel, takeEvery } from 'redux-saga';
import { call, cps, fork, put, race, select, take } from 'redux-saga/effects';
import { ipcRenderer, remote } from 'electron';
import { openFileSucceeded } from '../actions/EditorActions';
import { updateGamepads } from '../actions/GamepadsActions';
import { runtimeConnect, runtimeDisconnect } from '../actions/InfoActions';
import { peripheralDisconnect } from '../actions/PeripheralActions';

const dialog = remote.dialog;

/**
 * The electron showOpenDialog interface does not work well
 * with redux-saga's 'cps' for callbacks. To make things nicer, we
 * wrap the Electron dialog functionality in a promise,
 * which works well with redux-saga's 'call' for promises.
 *
 * @return {Promise} - fulfilled if user selects file, rejected otherwise
 */
function openFileDialog() {
  return new Promise((resolve, reject) => {
    dialog.showOpenDialog({
      filters: [{ name: 'python', extensions: ['py'] }],
    }, (filepaths) => {
      // If filepaths is undefined, the user did not specify a file.
      if (filepaths === undefined) {
        reject();
      } else {
        resolve(filepaths[0]);
      }
    });
  });
}

/**
 * Using Promise for Electron save dialog functionality for the same
 * reason as above.
 *
 * @return {Promise} - fulfilled with filepath once user hits save.
 */
function saveFileDialog() {
  return new Promise((resolve, reject) => {
    dialog.showSaveDialog({
      filters: [{ name: 'python', extensions: ['py'] }],
    }, (filepath) => {
      // If filepath is undefined, the user did not specify a file.
      if (filepath === undefined) {
        reject();
        return;
      }

      // Automatically append .py extension if they don't have it
      if (!filepath.endsWith('.py')) {
        resolve(`${filepath}.py`);
      }
      resolve(filepath);
    });
  });
}

/**
 * Using Promise for Electron message dialog functionality for the same
 * reason as above.
 *
 * @return {Promise} - fulfilled with button index.
 */
function unsavedDialog(action) {
  return new Promise((resolve, reject) => {
    dialog.showMessageBox({
      type: 'warning',
      buttons: [`Save and ${action}`, `Discard and ${action}`, 'Cancel action'],
      title: 'You have unsaved changes!',
      message: `You are trying to ${action} a new file, but you have unsaved changes to 
your current one. What do you want to do?`,
    }, (res) => {
      // 'res' is an integer corrseponding to index in button list above.
      if (res === 0 || res === 1 || res === 2) {
        resolve(res);
      } else {
        reject();
      }
    });
  });
}

/**
 * Simple helper function to write to a codefile and dispatch action
 * notifying store of the save.
 */
function* writeFile(filepath, code) {
  yield cps(fs.writeFile, filepath, code);
  yield put({
    type: 'SAVE_FILE_SUCCEEDED',
    code,
    filepath,
  });
}

function* saveFile(action) {
  const selector = (state) => ({
    filepath: state.editor.filepath,
    code: state.editor.editorCode,
  });
  const result = yield select(selector);
  let filepath = result.filepath;
  const code = result.code;
  // If the action is a "save as" OR there is no filepath (ie, a new file)
  // then we open the save file dialog so the user can specify a filename before saving.
  if (action.saveAs || !filepath) {
    try {
      filepath = yield call(saveFileDialog);
      yield* writeFile(filepath, code);
    } catch (e) {
      console.log('No filename specified, file not saved.');
    }
  } else {
    yield* writeFile(filepath, code);
  }
}

function* openFile(action) {
  const type = (action.type === 'OPEN_FILE') ? 'open' : 'create';
  const selector = (state) => ({
    savedCode: state.editor.latestSaveCode,
    code: state.editor.editorCode,
  });
  const result = yield select(selector);
  let res = 1;
  if (result.code !== result.savedCode) {
    res = yield call(unsavedDialog, type);
    if (res === 0) {
      yield* saveFile({
        type: 'SAVE_FILE',
        saveAs: false,
      });
    }
  }
  if (res === 0 || res === 1) {
    if (type === 'open') {
      try {
        const filepath = yield call(openFileDialog);
        const data = yield cps(fs.readFile, filepath, 'utf8');
        yield put(openFileSucceeded(data, filepath));
      } catch (e) {
        console.log('No filename specified, no file opened.');
      }
    } else if (type === 'create') {
      yield put(openFileSucceeded('', null));
    }
  } else {
    console.log(`File ${type} canceled.`);
  }
}

/**
 * This saga acts as a "heartbeat" to check whether we are still receiving
 * updates from Runtime.
 *
 * NOTE that this is different from whether or not the Ansible connection
 * is still alive.
 */
function* runtimeHeartbeat() {
  while (true) {
    // Start a race between a delay and receiving an UPDATE_STATUS action from
    // runtime. Only the winner will have a value.
    const result = yield race({
      update: take('UPDATE_STATUS'),
      timeout: call(delay, 1000), // The delay is 1000 ms, or 1 second.
    });

    // If update wins, we assume we are connected, otherwise disconnected.
    if (result.update) {
      yield put(runtimeConnect());
    } else {
      yield put(runtimeDisconnect());
    }
  }
}

/**
 * This saga removes peripherals that have not been updated by Runtime
 * recently (they are assumed to be disconnected).
 */
function* reapPeripheral(action) {
  const id = String(action.peripheral.uid.high) + String(action.peripheral.uid.low);
  // Start a race between a delay and receiving an UPDATE_PERIPHERAL action for
  // this same peripheral (per peripheral.id). Only the winner has a value.
  const result = yield race({
    peripheralUpdate: take((nextAction) => (
      nextAction.type === 'UPDATE_PERIPHERAL' && (String(nextAction.peripheral.uid.high)
      + String(nextAction.peripheral.uid.low)) === id
    )),
    timeout: call(delay, 3000), // The delay is 3000 ms, or 3 seconds.
  });

  // If the delay won, then we have not received an update for this peripheral
  // recently and remove it from our state.
  if (result.timeout) {
    yield put(peripheralDisconnect(id));
  }
}

const _timestamps = [0, 0, 0, 0];

function _needToUpdate(newGamepads) {
  return _.some(newGamepads, (gamepad, index) => {
    if (!_.isUndefined(gamepad) && (gamepad.timestamp > _timestamps[index])) {
      _timestamps[index] = gamepad.timestamp;
      return true;
    } else if (_.isUndefined(gamepad) && !_.isNull(_timestamps[index])) {
      _timestamps[index] = null;
      return true;
    }
    return false;
  });
}

function formatGamepads(newGamepads) {
  const formattedGamepads = {};
  // Currently there is a bug on windows where navigator.getGamepads()
  // returns a second, 'ghost' gamepad even when only one is connected.
  // The filter on 'mapping' filters out the ghost gamepad.
  _.forEach(_.filter(newGamepads, { mapping: 'standard' }), (gamepad, indexGamepad) => {
    if (gamepad) {
      formattedGamepads[indexGamepad] = {
        index: indexGamepad,
        axes: gamepad.axes,
        buttons: _.map(gamepad.buttons, 'value'),
      };
    }
  });
  return formattedGamepads;
}

/**
 * Repeatedly grab gamepad data, send it over Ansible to the robot, and dispatch
 * redux action to update gamepad state.
 */
function* ansibleGamepads() {
  while (true) {
    // navigator.getGamepads always returns a reference to the same object. This
    // confuses redux, so we use assignIn to clone to a new object each time.
    const newGamepads = _.assignIn({}, navigator.getGamepads());
    if (_needToUpdate(newGamepads)) {
      const formattedGamepads = formatGamepads(newGamepads);
      yield put(updateGamepads(formattedGamepads));

      // Send gamepad data to Runtime over Ansible.
      if (_.some(newGamepads)) {
        yield put({ type: 'UPDATE_MAIN_PROCESS' });
      }
    }

    yield call(delay, 50); // wait 50 ms before updating again.
  }
}

/**
 * Creates the ansibleReceiver eventChannel, which emits
 * data received from the main process.
 */
function ansibleReceiver() {
  return eventChannel((emitter) => {
    const listener = (event, action) => {
      emitter(action);
    };
    // Suscribe listener to dispatches from main process.
    ipcRenderer.on('dispatch', listener);
    // Return an unsuscribe function.
    return () => {
      ipcRenderer.removeListener('dispatch', listener);
    };
  });
}

/**
 * Takes data from the ansibleReceiver channel and dispatches
 * it to the store
 */
function* ansibleSaga() {
  try {
    const chan = yield call(ansibleReceiver);
    while (true) {
      const action = yield take(chan);
      // dispatch the action
      yield put(action);
    }
  } catch (e) {
    console.log(e.stack);
  }
}

/**
 * Send the store to the main process whenever it changes.
 */
function* updateMainProcess() {
  const stateSlice = yield select((state) => ({
    studentCodeStatus: true,
    gamepads: state.gamepads.gamepads,
  }));
  ipcRenderer.send('stateUpdate', stateSlice);
}

/**
 * The root saga combines all the other sagas together into one.
 */
export default function* rootSaga() {
  yield [
    takeEvery('OPEN_FILE', openFile),
    takeEvery('SAVE_FILE', saveFile),
    takeEvery('CREATE_NEW_FILE', openFile),
    takeEvery('UPDATE_PERIPHERAL', reapPeripheral),
    takeEvery('UPDATE_MAIN_PROCESS', updateMainProcess),
    fork(runtimeHeartbeat),
    fork(ansibleGamepads),
    fork(ansibleSaga),
  ];
}
