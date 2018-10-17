
var vmMenu = new Vue({
	el:'#menu',
	data:{
		menu:[
		{
			url: '/',
			display: '口算成绩上报',
			icon: 'fa fa-edit',			
		},
		{
			url: '/view',
			display: '成绩查看',
			icon: 'fa fa-dashboard',

		},
		{
			url: '/signout',
			display: '退  出',
			icon: 'fa fa-fw fa-sign-out'
		}]
	},
	methods:{
		isActive:function(m){
			return m.url == window.location.pathname;
		}
		
	}
	
});
	
