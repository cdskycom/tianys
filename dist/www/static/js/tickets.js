function getLocalDateString(){
        var t = new Date();
        var month = t.getMonth() + 1;
        var monthStr = month < 10 ? "0" + String(month): String(month);
        var dateStr = t.getDate() < 10 ? "0" + String(t.getDate()): String(t.getDate());
        var hourStr = t.getHours() < 10 ? "0" + String(t.getHours()): String(t.getHours());
        var minuteStr = t.getMinutes() < 10 ? "0" + String(t.getMinutes()): String(t.getMinutes());
        return t.getFullYear() + '-' + monthStr + '-' + dateStr + 'T' + hourStr + ':' + minuteStr;
}

var vm = new Vue({
	el:'#app',
	data:{
		submit: false, //是否可提交回单及派单数据标识
		validateerror: false,
		validatemessage:'',
		messageTitle: '',
		message: '',
		troubleWindowTitle: '创建工单', //创建、查看、编辑工单modal的标题
		troublesTitle: '所有工单', //工单列表的标题
		curTroubleLogs: '',
		providers: '',
		toNextProvider: '',  //接收工单的厂家id
		transitReply: '',  //派单备注
		finishReply: '',   //回单备注
		checkedTroubles: [], //复选框选中的工单号列表
		troubleCategories: [], //故障类型
		impactArea:[], //故障影响范围
		newTrouble: {
			report_channel: '',
			type: '',
			region: '',
			level: '0',
			description: '',
			impact: '',
			startTime: '',
			endTime: '',
			custid: '',
			mac: '',
			contact: '',
			contact_phone: '',
			status: 'ACCEPT',
			create_user: '',
			create_user_name: '',
			deal_user: '',
			deal_user_name: '',
			dealingtime: ''
			
		},
		troubles: {
			currentPage: 1,
			itemsPerPage: 10,
			status: 'ALL',  //ALL- 所有工单，ACCEPT-已创建未分派，DEALING-处理中，FINISHED-已完成
			totalItems: 0,
			totalPage: 1,
			troubleList: [],
			viewTrouble: false,
			editTrouble: false,
			addTrouble: false,

		},
		
		
	},
	computed:{
		hasFinishedPermission:function(){
			return userinfo.permission.indexOf('FIN') != -1;
		}
	},
	methods:{
		initNewTrouble:function(){
			that = this;
			console.log('initnewtrouble...');
			
			that.newTrouble = {
				report_channel: '',
				type: this.troubleCategories[0].name,
				region: '',
				level: '0',
				description: '',
				impact: this.impactArea[0].area,
				startTime: getLocalDateString(),
				endTime: '',
				custid: '',
				mac: '',
				contact: '',
				contact_phone: '',
				status: 'ACCEPT',
				create_user: '',
				create_user_name: '',
				deal_user: '',
				deal_user_name: '',
				dealingtime: '',

			};

			that.submit = false;
			that.curTroubleLogs = '';
			that.troubles.addTrouble = true;
			that.troubles.editTrouble = false;
			that.troubles.viewTrouble = false;
			that.troubleWindowTitle = '创建工单';
		},
		getTroubleCategory:function(){
			that = this;
			var troubleUrl = baseUrl + 'api/troubleticket/gettroublecategory';
			axios.get(troubleUrl).then(function(res){
				that.troubleCategories= res.data.categories;	
				
			});
			
		},
		getImpactArea:function(){
			that = this;
			var troubleUrl = baseUrl + 'api/troubleticket/getimpactarea';
			axios.get(troubleUrl).then(function(res){
				that.impactArea= res.data.areas;	
				
			});

		},
		createTroubleTicket:function(event){
			that = this;
			var url = baseUrl + "api/addtroubleticket";
			axios.post(url,{
					report_channel: this.newTrouble.report_channel,
					type: this.newTrouble.type,
					region: this.newTrouble.region,
					level: this.newTrouble.level,
					description: this.newTrouble.description,
					impact: this.newTrouble.impact,
					startTime: this.newTrouble.startTime,
					custid: this.newTrouble.custid,
					mac: this.newTrouble.mac,
					contact: this.newTrouble.contact,
					contact_phone: this.newTrouble.contact_phone,
					status: this.newTrouble.status,
					create_user: userinfo.uid,
					create_user_name: userinfo.username,
					deal_user: userinfo.uid,
					deal_user_name: userinfo.username,
					dealingtime: ''
				}).then(function(res){
					if(res.data.error){
					
						that.validateerror = true;
						that.messageTitle = "处理失败";
						
					}else{
						that.validateerror = false;
						that.messageTitle = "处理成功"
						
					}
					that.message = res.data.message;
					
					that.showResultBox();
				
			});

			
		},
		showResultBox:function(){
			$('#modal-message').modal('show');
			$('#modal-message').on('hidden.bs.modal', function (e) {
				if(that.validateerror && (that.troubles.viewTrouble || that.troubles.editTrouble || that.troubles.addTrouble)){
					$('#modal-createtrouble').modal('show');
				}else{
					location.reload();
				}
			});
		},
		
		troubleDetail:function(t){
			that = this;
			that.troubles.viewTrouble = true;
			that.troubles.editTrouble = false;
			that.troubles.addTrouble = false;
			that.troubleWindowTitle = '查看工单';
			that.newTrouble = t;
			that.curTroubleLogs = '';
			// $('#modal-createtrouble').on('hidden.bs.modal', function (e) {
			// 			that.initNewTrouble();
			// 		});
			//$('#collapseOne').collapse('hide');

		},
		doEditTrouble:function(){
			that = this;
			that.troubles.viewTrouble = false;
			that.troubles.editTrouble = true;
			that.troubles.addTrouble = false;
			that.troubleWindowTitle = '编辑工单';
		},

		changeStatus:function(status){
			that = this;
			that.troubles.status = status;
			that.troubles.currentPage = 1;
			var s = window.localStorage;
			s['troublestatus'] = status;
			if(status == 'ACCEPT'){
				that.troublesTitle = '待分派工单';
			}else if(status == 'DEALING'){
				that.troublesTitle = '在途工单';
			}else if(status == 'FINISHED'){
				that.troublesTitle = '已完成工单';
			}else{
				that.troublesTitle = '所有工单';
			}
			
			var troubleUrl = baseUrl + 'api/troubleticket/gettrouble?page=' + this.troubles.currentPage + '&items_perpage=' + 
			this.troubles.itemsPerPage + '&status=' + this.troubles.status;
			axios.get(troubleUrl).then(function(res){
				that.troubles.totalItems = res.data.totalitems;
				that.troubles.totalPage = res.data.totalpage;
				that.troubles.troubleList = res.data.troubles;

			});
		},

		getLogs:function(id){
			if(this.curTroubleLogs == ''){
				
				that = this;
				var url = baseUrl + 'api/troubleticket/getlogs?' + 'troubleid=' + id;
				axios.get(url).then(function(res){
					that.curTroubleLogs = res.data.logs;
				});
				
			}
			
		},

		//获取派单厂家
		doTransit:function(){
			that = this;
			var url = baseUrl + 'api/troubleticket/getprovider';
			axios.get(url).then(function(res){
				that.providers = res.data.providers;
				
			});

		},

		

		//任务工单处理 t-处理类型，TRANSIT派单 FINISHED回单
		dealTrouble:function(t, flag){
			that = this;
			//回单直接回给派单人所在部门,转派工单则直接使用选择的厂家
			nextprovider = this.toNextProvider;
			reply = this.transitReply;
			if(t == 'FINISHED'){
				reply = this.finishReply;
			}
			troubles = [this.newTrouble.id];
			if(flag == 'batch'){
				
				troubles = this.checkedTroubles;
				

			}
			
			var  params = new URLSearchParams();
			params.append('dealingtype',t);			
			params.append('nextprovider',nextprovider);
			params.append('reply',reply);
			params.append('uid',userinfo.uid);
			params.append('troubles',troubles);
			axios.post(baseUrl + 'api/troubleticket/dealingtroublebatch', params
				// {
				// 	troubleid: this.newTrouble.id,
				// 	dealingtype: t,
				// 	nextprovider: nextprovider,
				// 	reply: reply,
				// 	uid: userinfo.uid
				// }
				).then(function(res){
					if(res.data.error){
					
						that.validateerror = true;
						that.messageTitle = "处理失败";
						
					}else{
						that.validateerror = false;
						that.messageTitle = "处理成功"
						
					}
					that.message = res.data.message;
					that.showResultBox();
					
				
				}).catch(function(error){
					that.validateerror = true;
					that.messageTitle = "处理失败";
					if(error.response){
						that.message = "服务器处理失败" + error.response.status;
					}else{
						that.message = error.message;
					}
					that.showResultBox();
					// return Promise.reject(error);
				});
				that.submit = false;
				
			
		},
		//设置可提交数据标识
		doSubmit:function(){
			this.submit = true;
		},
		doDealTrouble:function(t, flag){
			that = this;
			if(flag == 'batch'){
				if(that.checkedTroubles.length < 1){	
					that.messageTitle = "处理失败";
					that.message = "请至少选择一个工单";
					that.showResultBox();
					return;
				}

			}
			if(t == "TRANSIT"){
				that.doTransit(); //获取派单厂家
				$('#modal-transit').modal('show');
				$('#modal-transit').on('hidden.bs.modal', function (e) {
					if(that.submit){
						that.dealTrouble(t, flag);
					}
				});

			}else if(t == "FINISHED"){
				$('#modal-finish').modal('show');
				$('#modal-finish').on('hidden.bs.modal', function (e) {
					if(that.submit){
						that.dealTrouble(t, flag);
					}
				});

			}


		},

		handletopage:function(playload){
				that = this;
				this.troubles.currentPage = playload.page;

				var troubleUrl = baseUrl + 'api/troubleticket/gettrouble?page=' + this.troubles.currentPage + '&items_perpage=' + 
					this.troubles.itemsPerPage + '&status=' + this.troubles.status;
				axios.get(troubleUrl).then(function(res){
					that.troubles.troubleList = res.data.troubles;

				});
				

		},
		handleitemschange:function(playload){
			that = this;
			this.troubles.itemsPerPage = playload.newitems;
			this.troubles.currentPage = 1;
			var troubleUrl = baseUrl + 'api/troubleticket/gettrouble?page=' + this.troubles.currentPage + '&items_perpage=' + 
				this.troubles.itemsPerPage + '&status=' + this.troubles.status;
			axios.get(troubleUrl).then(function(res){
				that.troubles.totalItems = res.data.totalitems;
				that.troubles.totalPage = res.data.totalpage;
				that.troubles.troubleList = res.data.troubles;

			});

		}
		
	},

	//初始化页面数据
	created: function () {
    	
    	that = this;
    	var s = window.localStorage;
    	status = s['troublestatus'];

    	if(status){
    		that.troubles.status = status;
    		if(status == 'ACCEPT'){
				that.troublesTitle = '待分派工单';
			}else if(status == 'DEALING'){
				that.troublesTitle = '在途工单';
			}else if(status == 'FINISHED'){
				that.troublesTitle = '已完成工单';
			}else{
				that.troublesTitle = '所有工单';
			}
    	}
		var troubleUrl = baseUrl + 'api/troubleticket/gettrouble?page=' + this.troubles.currentPage + '&items_perpage=' + 
			this.troubles.itemsPerPage + '&status=' + this.troubles.status;
		axios.get(troubleUrl).then(function(res){
			that.troubles.totalItems = res.data.totalitems;
			that.troubles.totalPage = res.data.totalpage;
			that.troubles.troubleList = res.data.troubles;

		});
		this.getTroubleCategory();
		this.getImpactArea();
  	},
	filters:{
		//日期格式化过滤器
		DateTimeFtt: TV_DateTimeFtt.formatter,
		//故障级别显示过滤器
		levelStr:function(str){
			switch(str){
				case '0': return '紧急故障';
				case '1': return '一般故障';
				case '2': return '感知问题';
				default: return '未知级别';
			}
		},
		statusStr:function(str){
			switch(str){
				case 'ACCEPT': return '待分派';
				case 'DEALING': return '在途';
				case 'FINISHED': return '已完成';
				default: return '未知状态';
			}
		},
		//长文本截取过滤器
		shortcutStr:function(val,length){
			if(val.length > length){
				return val.substr(0,length) + '...';
			}else{
				return val;
			}
		},
		convertType:function(val){
			switch(val){
				case 'CREATE': return '创建';
				case 'REPLY': return '退回';
				case 'TRANSIT': return '转派';
				case 'FINISHED': return '回复';
				default: return '未知动作';
			}
		}
		
	}
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