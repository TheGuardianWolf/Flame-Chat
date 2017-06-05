flame.controller('conversationsController', ['$scope', function($scope) {
    $scope.userList = [
        {
            title: 'Active',
            data: []
        },
        {
            title: 'Unreachable',
            data: []
        },
        {
            title: 'Unknown',
            data: []
        }
    ];
}]);