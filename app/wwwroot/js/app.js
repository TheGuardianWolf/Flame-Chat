var apiUrl = location.origin + "/local";

var apiRoute = function(list) {
    return apiUrl + '/' + list.join('/') + '/';
};

var flame = angular.module('flame', [
  'ngRoute',
  'ngAria',
  'ngTouch',
  'angular-loading-bar',
  'emguo.poller',
  'ngFileUpload',
  'presence',
  'luegg.directives'
])
.config( [
    '$compileProvider', '$routeProvider', '$locationProvider', 'pollerConfig',
    function( $compileProvider, $routeProvider, $locationProvider, poller ) {
        $compileProvider.aHrefSanitizationWhitelist(/^\s*(https?|ftp|mailto|data|ms-appx):/);

        // $locationProvider.html5Mode(true);
        
        poller.smart = true;

        $routeProvider
        .when('/', {
            templateUrl : 'views/auth.html.txt',
            controller  : 'authController'
        })

        .when('/conversations', {
            templateUrl : 'views/conversations.html.txt',
            controller  : 'conversationsController'
        })

        // .when('/contacts', {
        //     templateUrl: 'views/conversations.html.txt',
        //     controller: 'contactsController'
        // })

        .when('/profile', {
            templateUrl: 'views/profile.html.txt',
            controller: 'profileController'
        });
    }
]);

flame.factory('states', function($presence) {
    var states = {
        ACTIVE : 0, // enter this state immediately after user-action
        IDLE : { // initially, two seconds after the last keypress and when mouse- or touchevents occur this state will be active
            enter: 5000,
            initial: true
        },
        AWAY : 60000 
    };
    return $presence.init(states);
});
