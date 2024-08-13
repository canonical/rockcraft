'use strict';

const os = require('os')
const express = require('express')
const app = express()
const port = 8080
const host = '0.0.0.0'

app.listen(port, host, () => {
  console.log(`Serving by ${os.userInfo().username} on port ${port}`);
});
