"use strict";
const electron = require("electron");
electron.contextBridge.exposeInMainWorld("mizukagami", {
  version: process.env.npm_package_version ?? "0.1.0"
});
