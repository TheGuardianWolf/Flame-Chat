function copy(obj) {
  var js = JSON.stringify(obj);
  return(JSON.parse(js));
}
