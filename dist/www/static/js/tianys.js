var baseUrl = "http://127.0.0.1:8089/"
var strLengthInTable = 30; //表格内显示文本最大长度

TV_DateTimeFtt = {
    formatter: function(timeStr){
            day = ['天','一','二','三','四','五','六']
            var t = new Date(timeStr);
            var month = t.getMonth() + 1;
            var monthStr = month < 10 ? "0" + String(month): String(month);
            var dateStr = t.getDate() < 10 ? "0" + String(t.getDate()): String(t.getDate());
            var hourStr = t.getHours() < 10 ? "0" + String(t.getHours()): String(t.getHours());
            var minuteStr = t.getMinutes() < 10 ? "0" + String(t.getMinutes()): String(t.getMinutes());
            var dayOfWeek = day[t.getDay()]
            

            return '星期' + dayOfWeek + ' (' + t.getFullYear() + '-' + monthStr + '-' + dateStr + ')';
        }
}



Vue.component('my-pagenation',{
    props:{
        itemsPerPage: Number,
        totalPage: Number,
        currentPage: Number,
        totalItems: Number
    },
    computed: {
        
        //显示当前页附近的10页
        displayNumber: function(){

            var range = [];
            if (this.totalPage <= 10){
                for(var i = 1; i <= this.totalPage; i++){
                    range.push(i);
                    
                }
            }else{
                if((this.current + 5) > this.totalPage){
                  
                    for(var i=this.totalPage-9; i<=this.totalPage; i++){
                        range.push(i);
                    }

                }else if((this.current-5) <= 0){
                    for(var i=1; i<=10; i++){
                        range.push(i)
                    }
                }else{

                    for(var i=this.current-4; i<=this.current+5; i++){
                        range.push(i)
                    }
                }
            }
            return range
        }
    },
    data: function(){
        return {items: this.itemsPerPage, current:this.currentPage, newpage:this.currentPage}
         
    },
     template: '<div class="input-group input-group-sm pull-right">' + 
            '<span>合计:{{ totalItems }}条记录, 共{{ totalPage }} 页,每页</span>' +
            '<select class="tv-page-form" v-model="items" v-on:change="itemsChange" >' + 
            '<option value="5" selected="">5</option><option value="10" selected="">10</option><option value="15" selected="">15</option><option value="20" selected="">20</option></select>' + 
            '<span>条</span>' + 
            '<ul class="pagination pagination-sm no-margin">' +
            '<li><a href="#" v-on:click="toPrePage">«</a></li>' +
            
            '<li v-for="num in displayNumber" v-on:click="changePage(num)" class=paginate_button v-bind:class="{ \'active\': num==current }" ><a href="#">{{ num }}</a></li>' +
            
            '<li><a href="#" v-on:click="toNextPage">»</a></li>' + 
            '<span> 跳转至:</span>' +
            '<input type="text" v-model="newpage" size="5">' +
            '<button type="button" class="btn btn-info" v-on:click="toPage">Go</button>' +
            '</ul></div>' ,
    
    methods: {
        toPrePage: function(){
            this.$emit('topage', {page: (this.current-1)>=1? this.current -= 1 : this.current})

        },
        toNextPage: function(){
            this.$emit('topage', {page: (this.current+1)<=this.totalPage? this.current += 1 : this.current})
        },
        toPage:function(){
            this.current = this.newpage >=1 && this.newpage <=this.totalPage ? parseInt(this.newpage): this.current;
           
            this.$emit('topage',{page: this.current});

        },
        changePage:function(num,event){
            
            this.current = num;
            this.$emit('topage',{page:num});


        },
        //每页显示数量配置改变处理函数
        itemsChange:function(event){
            this.$emit('pageitemschange',{newitems: this.items});
            
        }
    }


})