/*
 * Defines the edit menu.
 */

import RendererBridge from '../RendererBridge';

const EditMenu = {
  label: 'Edit',
  submenu: [
    {
      label: 'Cut',
      accelerator: 'CommandOrControl+X',
      role: 'cut',
    },
    {
      label: 'Copy',
      accelerator: 'CommandOrControl+C',
      role: 'copy',
    },
    {
      label: 'Paste',
      accelerator: 'CommandOrControl+V',
      role: 'paste',
    },
    {
      label: 'Preferences',
      click() {
        RendererBridge.registeredWindow.webContents.send('open-preferences');
      },
    },
  ],
};

export default EditMenu;
