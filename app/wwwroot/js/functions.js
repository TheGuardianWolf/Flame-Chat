function copy(obj) {
  var js = JSON.stringify(obj);
  return(JSON.parse(js));
}

function capitalize(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}