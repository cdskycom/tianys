
var vm = new Vue({
	el:'#app',
	data:{
		providers:'',
		curProvider:''
			
	},
	
	methods:{
		selectProvider:function(p){
			that = this;
			that.curProvider = p;

		}
		
	},

	//初始化页面数据
	created: function () {
    	
    	that = this;
		var troubleUrl = baseUrl + 'api/troubleticket/getprovider';
		axios.get(troubleUrl).then(function(res){
			that.providers = res.data.providers;
			that.curProvider = that.providers[0];

		});
		
  	},
	
});
	

	// window.onload = function(){
	// 	if(ID){
	// 		axios.get('/api/users/' + ID).then(res=>{initVM(res.data.user,'edit')});
	// 	}
	// 	else{
	// 		initVM({
	// 			account:'',
	// 			password:'',
	// 			name:'',
	// 			is_admin:0
	// 		},'add')
	// 	}

	// }