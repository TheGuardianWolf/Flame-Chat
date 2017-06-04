Cache = {
  auth : {},
  userAccount : [],
  user : {},
  courses : [],
  enrollments : [],
  enrolledCourseIDs : [],
  assignmentFiles : [],
  tests : [],
  assignments : [],
  toDos : [],
  uncompletedToDos : [],
  completedToDos : [],
  enrolledCourses : [],
  freeCourses : [],
};

/**
 * You first need to create a formatting function to pad numbers to two digits…
 **/
function twoDigits(d) {
    if(0 <= d && d < 10) return "0" + d.toString();
    if(-10 < d && d < 0) return "-0" + (-1*d).toString();
    return d.toString();
}

/**
 * …and then create the method to output the date string as desired.
 * Some people hate using prototypes this way, but if you are going
 * to apply this to more than one Date object, having it as a prototype
 * makes sense.
 **/
Date.prototype.toMysqlFormat = function() {
    return this.getUTCFullYear() + "-" + twoDigits(1 + this.getUTCMonth()) + "-" + twoDigits(this.getUTCDate()) + " " + twoDigits(this.getUTCHours()) + ":" + twoDigits(this.getUTCMinutes()) + ":" + twoDigits(this.getUTCSeconds());
};

fromMysqlFormat = function(sqlDate) {
  // Split timestamp into [ Y, M, D, h, m, s ]
  var t = sqlDate.split(/[- :]/);
  // Apply each element to the Date function
  var d = new Date(t[0], t[1]-1, t[2], t[3], t[4], t[5]);
  return d;
};

function copy(obj) {
  var js = JSON.stringify(obj);
  return(JSON.parse(js));
}
