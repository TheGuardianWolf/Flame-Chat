flame.controller('profileController', ['$scope', '$http', function($scope, $http) {
    // Create view models for templating
    $scope.profile = {
        fullname: '',
        position: '',
        description: '',
        location: '',
        picture: ''
    };

    var userId = null;
    var formRetrieved = false;

    $scope.$watch('data.users', function() {
        if ($scope.data.users) {
            if (!userId) {
                currentUser = $scope.data.users.reachable.filter(function(user) {
                    return user.username === $scope.data.currentUser.username;
                });

                if (currentUser.length > 0) {
                    userId = currentUser[0].id;
                }
            }
        }
    });

    var updateProfile = function(newValue, oldValue) {
        if (!formRetrieved) {
            var profile = $scope.data.profiles.filter(function(profile) {
                return profile.userId === userId;
            });

            if (profile.length > 0) {
                profile = profile[0];

                $scope.profile.fullname = profile.fullname;
                $scope.profile.position = profile.position;
                $scope.profile.description = profile.description;
                $scope.profile.location = profile.location;
                $scope.profile.picture = profile.picture;
            } 
            formRetrieved = true;
        }
    };

    $scope.$watchCollection('data.profiles', updateProfile);

    var sendProfile = function() {
        var request = $http({
            method: 'POST',
            url: apiRoute(['profiles', 'post']),
            data: JSON.stringify({
                fullname: $scope.profile.fullname,
                position: $scope.profile.position,
                description: $scope.profile.description,
                location: $scope.profile.location,
                picture: $scope.profile.picture
            })
        });

        request.then(
            function success(response) {
                $.Notify({
                    caption: 'Success',
                    content: 'Profile updated on local server.',
                    type: 'success'
                });
            },
            function fail(response) {
                $.Notify({
                    caption: 'Error',
                    content: 'Unable to update profile, local server reports an error.',
                    type: 'alert'
                });
            }
        );

        return request;
    };
    $scope.sendProfile = sendProfile;
}]);