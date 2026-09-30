var express = require('express');
var fs = require('fs');
var router = express.Router();

router.get('/', function(req, res, next) {
  res.render('index', { title: 'Express' });
});

router.get('/write-data', function(req, res) {
  fs.writeFileSync('/app-data/expressjs-test.txt', 'written by expressjs\n');
  res.json(true);
});

module.exports = router;
