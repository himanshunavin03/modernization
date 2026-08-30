angular.module('sample').controller('dashboardController', function() {}).service('dashboardService', function($http) { return $http({url: '/api/summary'}); }).directive('chart', function() {});
