    $('input[type="range"]').rangeslider({
        onSlide: (pos,val) => setDuration(pos) 
    });