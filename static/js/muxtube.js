var MuxTube = function() {
  this.player = null;
  this.playingIndex = -1;
  this.playingId = '';
  this.tracks = null;
  this.currentTrackHeight = 0;
  this.width = $('ul').width();
  this.showingVideo = $('#display-video').attr('checked');
};

MuxTube.constants = {
  UNSTARTED: -1,
  ENDED: 0,
  PLAYING: 1,
  PAUSED: 2,
  BUFFERING: 3,
  CUED: 5,
  VIDEO_HEIGHT: 356,
  VIDEO_WIDTH: 425
};

MuxTube.utils = {
  urlForId: function(id) {
    return 'http://www.youtube.com/v/' + id +
      '?enablejsapi=1&playerapiid=ytplayer&version=3';
  },
  bind: function(f, obj) {
    return function() {
      return obj[f].apply(obj, arguments);
    };
  },
  secondsToTime: function(raw) {
    if (raw < 0) {
      return '0:00';
    }
    var minutes = raw / 60.0;
    var fmins = Math.floor(minutes);
    var seconds = Math.round(raw - (fmins * 60));
    if (seconds < 10) {
      seconds = '0' + seconds;
    }
    return fmins + ':' + seconds;
  }
}

// these are global for the player...
var onYouTubePlayerReady = null;
var onPlayerError = null;
var onPlayerStateChange = null;

MuxTube.prototype.initialize = function(initialID) {
  var params = { allowScriptAccess: "always" };
  var atts = { id: "theplayer" };
  var u = "http://www.youtube.com/apiplayer?&enablejsapi=1&playerapiid=player1";
  swfobject.embedSWF(u, "player", "425", "356", "8", null, null, params, atts);

  onYouTubePlayerReady = MuxTube.utils.bind('onPlayerReady', this);
  onPlayerError = MuxTube.utils.bind('onPlayerReady', this);
  onPlayerStateChange = MuxTube.utils.bind('onPlayerStateChange', this);
};

MuxTube.prototype.onInterval = function() {
  if (!(this.player)) {
    return;
  }

  var state = this.player.getPlayerState();
  switch (state) {
  case MuxTube.constants.PLAYING:
  case MuxTube.constants.BUFFERING:
    if (this.playingId) {
      var p = $('#progress-' + this.playingId);
      var loaded = this.player.getVideoBytesLoaded();
      var total = this.player.getVideoBytesTotal();
      var seconds = this.player.getCurrentTime();
      var duration = this.player.getDuration();
      var loading_width = Math.floor((loaded / total) * this.width);
      var indicator_width = Math.floor((seconds / duration) * this.width);
      if (loading_width >= this.width && seconds > '0:00') {
        $('#youtube-' + this.playingId + ' .loader').fadeOut('slow');
      }
      else {
        $('#youtube-' + this.playingId + ' .loader').width(loading_width);
      }

      if (indicator_width >= this.width && seconds > '0:00') {
        $('#youtube-' + this.playingId + ' .indicator').fadeOut('slow');
      }
      else {
        $('#youtube-' + this.playingId + ' .indicator').width(indicator_width);
      }

      p.html(MuxTube.utils.secondsToTime(seconds));
    }
    break;
  case MuxTube.constants.PAUSED:
    if (this.playingId) {
      var p = $('#progress-' + this.player.playingId)
      if (!p.hasClass('paused')) {
        p.addClass('paused');
      }
    }
    break;
  }
};

MuxTube.prototype.onPlayerReady = function(playerId) {
  this.player = document.getElementById('theplayer');
  this.tracks = $('#playlist li.track');
  var t = this;
  $('#playlist li.track').each(function (i, e) {
    var height = $(e).height();
    $(e).find('.loader').height(height + 9);
    $(e).find('.indicator').height(height + 9);
    $(e).click(function() {
      t.play(i);
    });
  });

  this.player.addEventListener('onStateChange', 'onPlayerStateChange');
  this.player.addEventListener('onError', 'onPlayerError');
  this.interval = setInterval(MuxTube.utils.bind('onInterval', this), 250);
  this.onInterval();
};

MuxTube.prototype.onPlayerError = function() {

};

MuxTube.prototype.onPlayerStateChange = function(newState) {

};

MuxTube.prototype.play = function(index) {
  this.tracks.find('.progress span').html('');
  this.playingId = '';
  this.playingIndex = -1;

  if (index >= 0 && index < this.tracks.length) {
    var track = this.tracks[index];
    var id = $(track).attr('id').split('-')[1];
    this.player.loadVideoById(id, 0);
    this.player.playVideo();
    this.playingIndex = index;
    this.playingId = id;
    if (this.showingVideo) {
      this.hideVideo();
      var currentHeight = $(track).height();
      var newHeight = currentHeight + MuxTube.constants.VIDEO_HEIGHT;
      var that = this;
      $(track).animate({height: newHeight}, 500, function() {
        $('#player-container').css({left: 300, top: 20});
        that.showVideo();
      });
    }
  }

};

MuxTube.prototype.showVideo = function() {
  $(this.player).height(MuxTube.constants.VIDEO_HEIGHT).width(MuxTube.constants.VIDEO_WIDTH);
};

MuxTube.prototype.hideVideo = function() {
  $(this.player).height(1).width(1);
}

MuxTube.prototype.toggleShowVideo = function() {
  if ($('#display-video').attr('checked')) {
    this.showVideo();
    this.showingVideo = true;
  }
  else {
    this.hideVideo();
    this.showingVideo = false;
  }
};

jQuery(document).ready(function($) {
  var muxtube = new MuxTube();
  muxtube.initialize();
  $('#display-video').click(function() {
    muxtube.toggleShowVideo();
  });
});