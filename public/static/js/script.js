var app = angular.module('BomCodigo', ['ngRoute', 'ngMaterial', 'ngAnimate', 'ngAria', 'ngCookies']);

/* Configuraçao do visual*/
app.config(function($mdThemingProvider) {
  // Cor do cabeçalho.
  $mdThemingProvider.theme('default')
    .primaryPalette('cyan')
    .accentPalette('orange')
    .warnPalette('orange');
});


/* Configuraçao de rotas*/
app.config(['$routeProvider', function($routerProvider){
	$routerProvider
		.when('/meus-repositorios', {
			controller: "ReposController",//"RepositoriosUsuarioController",
			templateUrl: 'templates/repositoriosUsuario.tmpl.html'
		})
		.when('/ranking-usuarios', {
			controller: "RankingUsuarioController",
			templateUrl: 'templates/ranking.tmpl.html'
		})
		.when('/ranking-repositorios', {
			controller: "RankingRepositorioController",
			templateUrl: 'templates/rankingRepositorio.tmpl.html'
		})
	  	.when('/', {
      		templateUrl: 'templates/inicio.tmpl.html'
    })
    .otherwise({
  		templateUrl: 'templates/pageNotFound.tmpl.html'
	});
}]);


/* Realiza requisiçao ajax */
app.factory('RankingAPI', function($http){
	var _getLista =  function(url){
		return $http.get(url);
	};
	return {
		getLista: _getLista
	};
});

/* Retorna o usuario logado no momento. */
app.factory('GetUsuario', function($cookies){
    var _getUsuario =  function(){
       return $cookies.get('login');
    };
    return {
       getUsuario: _getUsuario
    };
});


/* Controla ranking*/
app.controller('RankingUsuarioController', function($rootScope, $scope, RankingAPI, config){
	var url = config.baseURL + '/ranking';

	$scope.ranking = [];
	$scope.user = {};

	RankingAPI.getLista(url).then(function(response) {         
		var r = response.data;
		$scope.ranking = r;

		for (var i = 0; i < r.length; i++){  
			$scope.ranking[i]['posicao']  = i + 1;
			RankingAPI.getLista('https://api.github.com/users/'+ r[i].login).then(function(response) {  
				$scope.user[response.data.login] = response.data;
			});
		} 
	});
});

/* Controla ranking repositórios*/
app.controller('RankingRepositorioController', function($rootScope, $scope, RankingAPI, config){
	var url = config.baseURL + '/ranking/repos';

	$scope.ranking = [];

	RankingAPI.getLista(url).then(function(response) {         
		var r = response.data;
		$scope.ranking = r;

		for (var i = 0; i < r.length; i++){  
			$scope.ranking[i]['posicao']  = i + 1;
		} 
	});
});


/* Controla repositorios do usuario*/
app.controller('ReposController', function($http, $rootScope, $scope, $mdDialog, GetUsuario, RankingAPI, config, $cookies){
	$scope.repositorios = [];

  	var user = GetUsuario.getUsuario();

	if(user != ''){
		RankingAPI.getLista('https://api.github.com/users/'+ user +'/repos').then (function(response) {
		  $scope.repositorios = response.data;
		});
	}

	$scope.analisarRepositorio = function(ev, repositorio) {
		var url = config.baseURL + '/analysis/' + repositorio.html_url;
		$rootScope.nomeRepo = repositorio['name'];

		$mdDialog.show({
	      controller: DialogController,
	      contentElement: '#myDialog',
	      parent: angular.element(document.body),
	      targetEvent: ev,
	      clickOutsideToClose: false
	    });
	    
		RankingAPI.getLista(url).then(function(response){
			$rootScope.informacoes = response.data;
			$mdDialog.show({
				controller: DialogController,
				templateUrl: 'templates/tabDialog.tmpl.html',
				parent: angular.element(document.body),
				targetEvent: ev,
				clickOutsideToClose:false
			});
		});
	};
 
	function DialogController($scope, $mdDialog) {
		$scope.info = $rootScope.informacoes;
		$scope.nomeRepositorio = $rootScope.nomeRepo;

		$scope.cancel = function() {
			$mdDialog.cancel();
		};
	}

});

/* Controla login */
app.controller("LoginController", function($scope, $http, $window, $cookies, config){
  $scope.login = '';
  $scope.avatar = ''; 

  $scope.is_autenticado = function(){
    var user = firebase.auth().currentUser;
    
    if (user){
      $scope.user = user.displayName;
      $scope.avatar = user.photoURL;
      return true;
    }else
      return false;
  }

  $scope.entrar = function(){
	var provider = new firebase.auth.GithubAuthProvider(); 
	firebase.auth().signInWithPopup(provider).then(function(result) {

	// This gives you a GitHub Access Token. You can use it to access the GitHub API.
	var token = result.credential.accessToken;
	repositoriosGit = config.baseURLGIT + '/user?access_token=' + token;

	$http.get(repositoriosGit).then(function(response) {
		// Armazena o usuario logado no cookie.
		$cookies.put('login', response.data.login);

		// Atualiza a pagina apos login.
		$window.location.reload();
		});

		}).catch(function(error) {
		// Handle Errors here.
		var errorCode = error.code;
		var errorMessage = error.message;
	});
  }

  $scope.sair = function(){
    firebase.auth().signOut().then(function() {
      $cookies.put('login', '')
      $window.location.reload();  
    }, function(error) {
      alert('Erro logout');
    });
  }
})
