webpackJsonp([39],{"3dO+":function(t,e){},"9Sjc":function(t,e,a){"use strict";Object.defineProperty(e,"__esModule",{value:!0});var l={data:function(){return{tableData:[{date:"2016-05-02",name:"王小虎",address:"上海市普陀区金沙江路 1518 弄"}],dialogTableVisible:!1,dialogFormVisible:!1,form:{name:""},formLabelWidth:"120px"}},methods:{Fnval:function(){this.dialogFormVisible=!0}}},i={render:function(){var t=this,e=t.$createElement,a=t._self._c||e;return a("div",[a("div",{staticClass:"title"},[t._v("\n      设备台账\n  ")]),t._v(" "),a("el-alert",{attrs:{title:"台账信息的初始化工作请到系统设置-设备台账初始化中进行设置 注：修改即生效",type:"warning",closable:!1}}),t._v(" "),a("div",{staticClass:"tabBox"},[a("el-table",{staticStyle:{width:"100%"},attrs:{data:t.tableData,fit:!0}},[a("el-table-column",{attrs:{prop:"date",label:"字段名",width:"180"}}),t._v(" "),a("el-table-column",{attrs:{prop:"name",label:"值",width:"180"},scopedSlots:t._u([{key:"default",fn:function(e){return[a("div",{staticClass:"valCSS",on:{click:function(e){t.dialogFormVisible=!0}}},[t._v(" "+t._s(""==t.form.name?"点击输入值":t.form.name))]),t._v(" "),a("el-dialog",{attrs:{title:"填写值",visible:t.dialogFormVisible},on:{"update:visible":function(e){t.dialogFormVisible=e}}},[a("el-form",{attrs:{model:t.form}},[a("el-form-item",{attrs:{label:"","label-width":t.formLabelWidth}},[a("el-input",{attrs:{autocomplete:"off"},model:{value:t.form.name,callback:function(e){t.$set(t.form,"name",e)},expression:"form.name"}})],1)],1),t._v(" "),a("div",{staticClass:"dialog-footer",attrs:{slot:"footer"},slot:"footer"},[a("el-button",{on:{click:function(e){t.dialogFormVisible=!1}}},[t._v("取 消")]),t._v(" "),a("el-button",{attrs:{type:"primary"},on:{click:function(e){t.dialogFormVisible=!1}}},[t._v("确 定")])],1)],1)]}}])}),t._v(" "),a("el-table-column",{attrs:{prop:"address",label:"单位"}})],1)],1)],1)},staticRenderFns:[]};var o=a("VU/8")(l,i,!1,function(t){a("3dO+")},"data-v-523b9432",null);e.default=o.exports}});
//# sourceMappingURL=39.a36e14110d1c1c7871ec.js.map