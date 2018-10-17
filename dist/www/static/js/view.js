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
		validateerror: false,
		messageTitle: '',
		message: '',
		days: 6,
		cals: '',
		detailOrderby: 'user,cal_date',
		statisticOrderby: 'asc',
		statisticCals: '',
		stime:'',
		etime:'',
		tableTitle:'最近 7 天口算成绩'

	},
	methods:{
		
		adjustDays:function(){
			
			if(this.stime == '' || this.etime == ''){
				this.validateerror = true;
				this.messageTitle = '时间格式错误';
				this.message = '开始时间或结束时间不正确';
				$('#modal-message').modal('show');
				return;
			}
			var stime = this.stime;
			var etime = this.etime;
			this.tableTitle = TV_DateTimeFtt.formatter(this.stime) + '至' + TV_DateTimeFtt.formatter(this.etime)
				 + '口算成绩';
			this.getRecentCals(stime, etime);
			this.getStatisticCals(stime,etime);
		},
		getRecentCals:function(stime, etime){
			that = this;
			var url = 'api/math/getmathoralcal?uid=' +userinfo.uid + '&starttime=' +
				stime + '&endtime=' + etime + '&orderby=' + this.detailOrderby;
			axios.get(url).then(function(res){
					that.cals = res.data.cals;

				});
		},
		getStatisticCals:function(stime, etime){
			that = this;
			var url = 'api/math/getstatistic?uid=' +userinfo.uid + '&starttime=' +
				stime + '&endtime=' + etime + '&orderby=' + this.statisticOrderby;
			axios.get(url).then(function(res){
					that.statisticCals = res.data.cals;

				});
		}
		
	},
	created:function(){
		var stime = getLocalDateString(-this.days);
		var etime = getLocalDateString(0);
		this.getRecentCals(stime,etime);
		this.getStatisticCals(stime,etime);
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
	
