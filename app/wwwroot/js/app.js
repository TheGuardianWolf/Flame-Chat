var apiUrl = location.origin + "/local";

var apiRoute = function(list) {
    return apiUrl + '/' + list.join('/') + '/';
};

var flame = angular.module('flame', [
  'ngRoute',
  'ngAria',
  'ngTouch',
  'angular-loading-bar',
  'emguo.poller'
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

        .when('/contacts', {
            templateUrl: 'views/conversations.html.txt',
            controller: 'contactsController'
        })

        .when('/profile', {
            templateUrl: 'views/profile.html.txt',
            controller: 'profileController'
        });
    }
]);
