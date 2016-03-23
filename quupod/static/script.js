$(document).ready(function(){
  namespace = '/main'; // change to an empty string to use the global namespace

  // Socket.io documentation recommends sending an explicit package upon
  // connection. This is especially important when using the global namespace
  var socket = io.connect('http://' + document.domain + ':' + location.port + namespace);

  /*
   * EVENT HANDLERS
   * These receive data from server and update pages client-side.
   */

  // Update queue positions for all users
  socket.on('update position', function(msg) {
    for (i=0; i<len(msg.positions); i++) {
      console.log(msg.positions[i]);
    }
  });

  // Update student page with ttr, number of requests
  socket.on('update student page', function(msg) {

  });

  // Update staff page with ttr, number of requests, help needed
  socket.on('update staff page', function(msg) {

  });

  // Event handler for new connections
  socket.on('connect', function() {
    socket.emit('resolve', {data: 'I\'m connected!'});
  });

  /*
   * FORM HANDLERS
   * These send data from the client to the server.
   */

  $('form.resolve-socket').submit(function(event) {
    socket.emit('resolve', {data: $(this).data('inquiry')});
    $(this).submit();
  });
});
