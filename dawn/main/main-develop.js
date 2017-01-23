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
    width: 500,
    height: 500,
  });

  // connects to window's redux state and dispatcher
  RendererBridge.registerWindow(mainWindow);

  mainWindow.maximize();
  mainWindow.loadURL(`file://${__dirname}/../static/index.html`);
  fieldControlWindow.loadURL(`file://${__dirname}/../static/indexFC.html`);

  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  const menu = Menu.buildFromTemplate(Template);
  Menu.setApplicationMenu(menu);
});
