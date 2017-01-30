/**
 * Entrypoint for main process of Dawn.
 */

import { app, BrowserWindow, Menu } from 'electron';
import RendererBridge from './RendererBridge';
import Template from './MenuTemplate/Template';
import './ansible/Ansible';

let mainWindow; // the window which displays main editor, peripherals and gamepads
let fieldControlWindow; // the window which displays field control

app.on('window-all-closed', () => {
  app.quit();
});

app.on('ready', () => {
  mainWindow = new BrowserWindow();
  fieldControlWindow = new BrowserWindow({
    width: 300,
    height: 200,
    transparent: true,
    frame: false,
    parent: mainWindow,
  });
  fieldControlWindow.setHasShadow(false);

  // connects to window's redux state and dispatcher
  RendererBridge.registerWindow(mainWindow);

  mainWindow.maximize();
  mainWindow.loadURL(`file://${__dirname}/../static/index.html`);
  fieldControlWindow.loadURL(`file://${__dirname}/../static/indexFC.html`);

  mainWindow.on('closed', () => {
    mainWindow = null;
    fieldControlWindow = null;
  });

  const menu = Menu.buildFromTemplate(Template);
  Menu.setApplicationMenu(menu);

  /* setInterval(() => {
    fieldControlWindow.setAlwaysOnTop(true);
  }, 1); */
});
