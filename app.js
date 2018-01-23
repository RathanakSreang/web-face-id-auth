var express = require("express");
var app = new express();
// Set port, default 8888
var port = process.env.PORT || 8888;

var server = require('http').createServer(app);
var io = require("socket.io")(server);
var Log = require("log"),
  log = new Log("debug");


app.use(express.static( __dirname + "/templates" ));

app.get("/", function(req, res) {
  res.redirect("index.html");
});

server.listen(port, function() {
  log.info("Listening port %s", port);
});

io.on("connection", function(socket) {
  log.info("New client");
  socket.on("stream", function(img) {
    socket.broadcast.emit("stream", img);
  });
});
