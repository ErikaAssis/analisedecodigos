var app = angular.module('BomCodigo', ['ngRoute', 'ngMaterial', 'ngAnimate', 'ngAria', 'ngCookies']);

/* Configuração do tema*/
app.config(function($mdThemingProvider) {
  $mdThemingProvider.theme('default').primaryPalette('blue').accentPalette('orange').warnPalette('orange');
  $mdThemingProvider.theme('dark-orange').backgroundPalette('orange').dark();
  $mdThemingProvider.theme('dark-purple').backgroundPalette('deep-purple').dark();
  $mdThemingProvider.theme('dark-blue').backgroundPalette('blue').dark();
  $mdThemingProvider.theme('dark-red').backgroundPalette('red').dark();
  $mdThemingProvider.theme('dark-green').backgroundPalette('green').dark();
});


/*Configuração de rotas*/
app.config(['$routeProvider', function($routerProvider){
	$routerProvider
		.when('/', {
			controller: 'LoginController',
			templateUrl: 'templates/inicio.tmpl.html'
		})
		.when('/meus-repositorios', {
			controller: "ReposController",
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
	    .otherwise({
	    	redirectTo: '/'
	  		//templateUrl: 'templates/pageNotFound.tmpl.html'
		});
}]);


/*Controla login e logout*/
app.controller("LoginController", function($scope, $rootScope, $http, $window, $cookies, $route, $location, config){
	
	
	$scope.is_autenticado = function(){
		var user = firebase.auth().currentUser;
		
		// firebase.auth().onAuthStateChanged(function(user) {
		    
		//     if (user) {
		//       // User is signed in.
		//       //console.log('logado')
		//       	$scope.t = true;
		//     	
		//     } else {
		//       // User is signed out.
		//      	//console.log('não')
		//      	$scope.t = false;
		//     }
		// })

		// if (user){
		
		// 	//return true;
		// }else
	
		if ($cookies.get('login') == '')
			return false;
		
		if (user != null){
			$scope.user = user.displayName;
			$scope.avatar = user.photoURL;
		}
		return true
	}
	
	
	//alert('Logado: ' + !!firebase.auth().currentUser)
	$scope.entrar = function(){
		//alert('Logado: ' + !!firebase.auth().currentUser)
		
		if (!firebase.auth().currentUser) {

			var provider = new firebase.auth.GithubAuthProvider(); 

			firebase.auth().signInWithPopup(provider).then(function(result) {
				$rootScope.token = result.credential.accessToken;
				
				// Obtém repositórios
				repositoriosGit = config.baseURLGIT + '/user?access_token=' + $rootScope.token;

				$http.get(repositoriosGit).then(function(response) {
					$cookies.put('login', response.data.login);
					$cookies.put('token', result.credential.accessToken);
					//$window.location.reload();
			})});
		}
	}

	$scope.sair = function(){
		firebase.auth().signOut().then(function() {
			$cookies.put('login', '')
			$window.location.href = '/'
		}, function(error) {
			alert('Erro logout');
		});
	}
});




/*Realiza requisição*/
app.factory('RankingAPI', function($http){
	var _getLista =  function(url){
		return $http.get(url);
	};
	return {
		getLista: _getLista
	};
});

/*Retorna o usuário*/
app.factory('GetUsuario', function($cookies){
    var _getUsuario =  function(){
       return $cookies.get('login');
    };
    return {
       getUsuario: _getUsuario
    };
});


/*Controla ranking de usuário*/
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

/*Controla ranking de repositórios*/
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


/*Controla repositórios do usuário*/
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
		var urlRanking = config.baseURL + '/ranking',
			urlRankingRepositorios = config.baseURL + '/ranking/repos';

		$scope.ranking = [];
		$scope.rank = [];
		$scope.user = {};
		$scope.info = $rootScope.informacoes;
		$scope.nomeRepositorio = $rootScope.nomeRepo;
		$scope.nomeUsuario = GetUsuario.getUsuario();

		RankingAPI.getLista(urlRanking).then(function(response) {         
			var r = response.data;
			$scope.ranking = r;

			for (var i = 0; i < r.length; i++){  
				$scope.ranking[i]['posicao']  = i + 1;
				RankingAPI.getLista('https://api.github.com/users/'+ r[i].login).then(function(response) {  
					$scope.user[response.data.login] = response.data;
				});
			} 
		});

		RankingAPI.getLista(urlRankingRepositorios).then(function(response) {         
			var r = response.data;
			$scope.rank = r;

			for (var i = 0; i < r.length; i++){  
				$scope.rank[i]['posicao']  = i + 1;
			} 
		});

		$scope.cancel = function() {
			$mdDialog.cancel();
		};
	}
});



