var apiUrl = "http://localhost:8080/local";

var apiRoute = function(list) {
    return apiUrl + '/' + list.join('/') + '/';
};

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
            // use the HTML5 History API
        //$locationProvider.html5Mode(true);
    }
]);
