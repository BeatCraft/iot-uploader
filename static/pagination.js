function pagination(c, m) {
  let current = c,
    last = m,
    delta = 2,
    left = current - delta,
    right = current + delta + 1,
    range = [],
    rangeWithDots = [],
    l;

  for (let i = 1; i <= last; i++) {
    if (i == 1 || i == last || i >= left && i < right) {
      range.push(i);
    }
  }

  for (let i of range) {
    if (l) {
      if (i - l === 2) {
        rangeWithDots.push(l + 1);
      } else if (i - l !== 1) {
        rangeWithDots.push('...');
      }
    }
    rangeWithDots.push(i);
    l = i;
  }

  let urlPrev = new URL(location);
  urlPrev.searchParams.set('page', Math.max(c-1, 1));

  var ul = $('<ul class="pagination justify-content-center">');
  ul.append(
    $('<li class="page-item">')
      .append($('<a class="page-link" aria-label="Previous">')
      .attr('href', urlPrev)
      .append("&laquo;")
    )
  );

  for (let i of rangeWithDots) {
    if (i === '...') {
      ul.append(
        $('<li class="page-item">').append(
          $('<a class="page-link disable" >').append('...')
        )
      );
    } else {
      let urlPage = new URL(location);
      urlPage.searchParams.set('page', i);

      var li = $('<li class="page-item">').append(
        $('<a class="page-link" >')
          .attr('href', urlPage)
          .append(i)
      );
      if (i === c) {
        li.addClass('active');
      }
      ul.append(li);
    }
  }

  let urlNext = new URL(location);
  urlNext.searchParams.set('page', Math.min(c+1, m));

  ul.append(
    $('<li class="page-item">')
      .append($('<a class="page-link" href="#" aria-label="Next">')
      .attr('href', urlNext)
      .append("&raquo;")
    )
  );

  return $('<nav aria-label="Page navigation">').append(ul);
}

$(function() {
    var nav = pagination({{ page }}, {{ total_page }});
    $(".pagenav").append(nav);
});

