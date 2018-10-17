function refresh() {
    var
        t = new Date().getTime(),
        url = location.pathname;
    if (location.search) {
        url = url + location.search + '&t=' + t;
    }
    else {
        url = url + '?t=' + t;
    }
    location.assign(url);
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
     template: '<div class="tv-pagenation">' + '<ul class="uk-pagination" uk-margin>' +
            '<span>合计:{{ totalItems }}条记录, 共{{ totalPage }} 页,每页</span>' +
            '<select class="tv-page-form" v-model="items" v-on:change="itemsChange" >' + 
            '<option value="5" selected="">5</option><option value="10" selected="">10</option><option value="15" selected="">15</option><option value="20" selected="">20</option></select>' + 
            '<span>条</span>' + 
            
            '<li><a href="#" v-on:click="toPrePage"><span uk-pagination-previous></span></a></li>' +
            
            '<li v-for="num in displayNumber" v-on:click="changePage(num)" ><a href="#"><span v-bind:class="{\'tv-page-active\' : num==current }">{{ num }}</span></a></li>' +
            
            '<li><a href="#" v-on:click="toNextPage"><span uk-pagination-next></span></a></li>' + 
           
            '<input type="text" v-model="newpage" size="5">' +
            '<button  v-on:click="toPage">Go</button>' +
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