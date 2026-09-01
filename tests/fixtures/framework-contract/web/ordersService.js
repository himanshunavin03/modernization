angular.module('demo').service('ordersService', function ($http) {
  this.get = function () { return $http.get('/api/orders/42'); };
  this.dynamic = function (id) { return $http.get('/api/orders/' + id); };
});
