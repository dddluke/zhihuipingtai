webpackJsonp([63],{KEfY:function(t,e,n){"use strict";Object.defineProperty(e,"__esModule",{value:!0});var a=n("Dd8w"),i=n.n(a),s=n("w7XY"),o=n("NYxO"),l={data:function(){return{tableData:[],total:0,currentPage:1,PageSize:7}},methods:{handleClick:function(t){this.$router.push({path:"/bkIndex/newsDetails",query:{k_id:t,k_type:"行业资讯"}})},FnAdd:function(){this.$router.push({path:"/bkIndex/newsDet",query:{k_id:-1}})},knowledgelistv2:function(){var t=this;s.a.knowledgelistv2({page:this.currentPage,per_page:this.PageSize}).then(function(e){if(e.data.code[0]="200"){var n=[];e.data.data.forEach(function(t){t.fields.k_id=t.pk,n.push(t.fields)}),t.tableData=n,t.total=e.data.datacount}})},handleCurrentChange:function(t){this.currentPage=t,this.knowledgelistv2()},gotoeditknowledge:function(t){this.$router.push({path:"/bkIndex/newsDet",query:{k_id:t}})},Fndeleteknowledge:function(t){var e=this;s.a.deleteknowledge({user_id:this.buserInfo.user_id,k_id:t}).then(function(t){(t.data.code[0]="200")&&(e.$message.success(t.data.message[0]),e.knowledgelistv2())})}},mounted:function(){this.knowledgelistv2()},computed:i()({},Object(o.c)(["buserInfo"]))},r={render:function(){var t=this,e=t.$createElement,n=t._self._c||e;return n("div",[n("div",{staticClass:"title"},[t._v("\n    更新行业资讯\n  ")]),t._v(" "),n("div",{staticClass:"WOBox"},[n("el-button",{attrs:{type:"warning"},on:{click:function(e){return t.FnAdd()}}},[t._v("新增")]),t._v(" "),n("el-divider"),t._v(" "),n("el-table",{staticStyle:{width:"100%"},attrs:{data:t.tableData,"show-header":!1}},[n("el-table-column",{attrs:{label:"历史发布"},scopedSlots:t._u([{key:"default",fn:function(e){return[n("div",{staticClass:"titnews"},[t._v(t._s(e.row.k_title))]),t._v(" "),n("div",{staticClass:"xxx"},[t._v(t._s(t._f("rephtml")(e.row.k_content)))]),t._v(" "),n("div",{staticClass:"tiemnews"},[t._v(t._s(t._f("toTime")(e.row.k_date)))])]}}])}),t._v(" "),n("el-table-column",{attrs:{label:"操作",width:"180",align:"right"},scopedSlots:t._u([{key:"default",fn:function(e){return[n("el-button",{attrs:{type:"text",size:"small"},on:{click:function(n){return t.handleClick(e.row.k_id)}}},[t._v("查看")]),t._v(" "),n("el-button",{attrs:{type:"text",size:"small"},on:{click:function(n){return t.gotoeditknowledge(e.row.k_id)}}},[t._v("编辑")]),t._v(" "),n("el-button",{attrs:{type:"text",size:"small"},on:{click:function(n){return t.Fndeleteknowledge(e.row.k_id)}}},[t._v("删除")])]}}])})],1),t._v(" "),n("el-pagination",{attrs:{background:"",layout:"prev, pager, next","current-page":t.currentPage,"page-size":t.PageSize,total:t.total},on:{"current-change":t.handleCurrentChange}})],1)])},staticRenderFns:[]};var d=n("VU/8")(l,r,!1,function(t){n("godh")},"data-v-0c97c932",null);e.default=d.exports},godh:function(t,e){}});
//# sourceMappingURL=63.7de1e21c2d5c171a2f8e.js.map