var contoso = angular.module('contoso', [
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

        var options = {applicationName:'Contoso University'};
        // Configuration options are described below

        $routeProvider
            .when('/', {
                templateUrl : 'views/auth.html',
                controller  : 'authController'
            })

            .when('/overview', {
                templateUrl : 'views/overview.html',
                controller  : 'overviewController'
            })
            // use the HTML5 History API
        //$locationProvider.html5Mode(true);
    }
]);
