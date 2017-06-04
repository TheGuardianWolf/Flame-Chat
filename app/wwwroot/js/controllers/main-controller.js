contoso.controller('mainController', ['$scope', '$http', '$location', function ($scope, $http, $location) {
    $scope.state = {
        loading: false,
        authenticated: false,
        sidebarCompact: true,
        ajaxBusy: false,
    };

    if ($scope.state.authenticated === false) {
        $location.url('');
    }

    $scope.parseDate = function (dateString) {
        return Date.parse(dateString).toString("dddd, MMMM dd, yyyy h:mm:ss tt");
    };

    $scope.toggleSidebar = function () {
        if ($scope.state.sidebarCompact) {
            $scope.state.sidebarCompact = false;
        } else {
            $scope.state.sidebarCompact = true;
        }
    };

    $scope.requests = function (type, route, data) {
        if (data === undefined) {
            data = $.param('');
        }
        var request = $http({
            method: type,
            url: 'https://university-contoso-api.azurewebsites.net/api/' + route.split('.').join('/'),
            headers: {
                'Accept': 'application/json',
            },
            'data': data
        });
        return request;
    };
}]);