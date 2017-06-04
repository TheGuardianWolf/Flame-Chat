var apiUrl = "http://localhost:8080/local";

var flame = angular.module('flame', [
  'ngRoute',
  'ngAria',
  'ngTouch',
  'angular-loading-bar',
])
.config( [
    '$compileProvider', '$routeProvider', '$locationProvider',
    function( $compileProvider, $routeProvider, $locationProvider )
    {
        $compileProvider.aHrefSanitizationWhitelist(/^\s*(https?|ftp|mailto|data|ms-appx):/);
        // Configuration options are described below

        $routeProvider
            .when('/', {
                templateUrl : 'views/auth.html',
                controller  : 'authController'
            })

            .when('/conversations', {
                templateUrl : 'views/split-pane.html',
                controller  : 'conversationsController'
            })

            .when('/contacts', {
                templateUrl: 'views/split-pane.html',
                controller: 'contactsController'
            })

            .when('/profile', {
                templateUrl: 'views/profile.html',
                controller: 'profileController'
            })
            // use the HTML5 History API
        //$locationProvider.html5Mode(true);
    }
]);
