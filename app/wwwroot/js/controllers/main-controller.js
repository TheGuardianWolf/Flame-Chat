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
}]);