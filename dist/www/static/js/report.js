function getLocalDateString(days){
        var t = new Date();
        t.setDate(t.getDate() + days);
        var month = t.getMonth() + 1;
        var monthStr = month < 10 ? "0" + String(month): String(month);
        var dateStr = t.getDate() < 10 ? "0" + String(t.getDate()): String(t.getDate());
        return t.getFullYear() + '-' + monthStr + '-' + dateStr;
}

var vm = new Vue({
	el:'#app',
	data:{
		calDate: getLocalDateString(0),
		consumingTime:'',
		minutes: 0,
		seconds: 0,
		errors: 0,
		validateerror: false,
		messageTitle: '',
		message: '',
		days: 6,
		newDays: 7,
		cals: ''

	},
	methods:{
		submitCal:function(){
			that = this;
			that.consumingTime = parseInt(that.minutes) * 60 + parseInt(that.seconds);
			that.errors = parseInt(that.errors);
			console.log('hi there:' + that.consumingTime);
			axios.post('api/addmathoralcal',{
					uid: userinfo.uid,
					caldate: that.calDate,
					consumingtime: that.consumingTime,
					errorcount: that.errors
				}).then(function(res){
					if(res.data.error){
					
						that.validateerror = true;
						that.messageTitle = "处理失败";
						
					}else{
						that.validateerror = false;
						that.messageTitle = "处理成功"
						
					}
					that.message = res.data.message;
					$('#modal-message').modal('show');
					$('#modal-message').on('hidden.bs.modal', function (e) {
						that.getRecentCals(-that.days)
					});

								
			});
			
		},
		adjustDays:function(){
			this.days = this.newDays - 1;
			this.getRecentCals(-this.days);
		},
		getRecentCals:function(days){
			that = this;
			var url = 'api/math/mathoralcals/' + userinfo.uid + '?starttime=' +
				getLocalDateString(days) + '&endtime=' + getLocalDateString(0);
			axios.get(url).then(function(res){
					that.cals = res.data.cals;

				});
		}
		
	},
	created:function(){
		this.getRecentCals(-this.days)
	},
	
	filters:{
		//日期格式化过滤器
		DateTimeFtt: TV_DateTimeFtt.formatter,
		//故障级别显示过滤器
		consumingTimeToStr:function(t){
			return parseInt(t/60) + ":" + (t % 60)
		}
		
		
	}
});
	
