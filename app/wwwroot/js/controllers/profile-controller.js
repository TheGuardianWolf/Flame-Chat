flame.controller('profileController', ['$scope', function($scope) {
    // Create view models for templating
    $scope.showContent = function() {
        return $scope.selectedModel !== null;
    }
    $scope.selectedModel = null;
    $scope.selectModel = function(model) {
        var filter = function(obj) {
            return obj.sender == model.username || obj.destination == model.username;
        };

        var content = $scope.data.messages
        .filter(relatedFilter)
        .forEach(function(message) {
            message.ngId = 'm' + String(message.id);
        })
        .concat(
            $scope.data.files
            .filter(relatedFilter)
            .forEach(function(file) {
                file.ngId = 'f' + String(file.id);
                file.href = 'data:' + file.content_type +  ';base64,' + file.file;
            })
        )
        .sort(function(a, b) {
            return a.stamp - b.stamp;
        });

        $scope = selectedModel = {
            model: model,
            content: content
        };
    };
}]);