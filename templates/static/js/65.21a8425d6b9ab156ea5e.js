webpackJsonp([65],{"2Uzb":function(e,t,a){"use strict";Object.defineProperty(t,"__esModule",{value:!0});var s=a("Dd8w"),r=a.n(s),i=a("w7XY"),n=a("NYxO"),l={data:function(){return{tableDatareRE:[],dialogFormVisible:!1,ADDtableData:[],tableDatareREget:[],AdialogFormVisible:!1,ruleForm:{staff_name:"",staff_phone:"",staff_password:""},rules:{staff_name:[{required:!0,message:"请输入活动名称",trigger:"blur"},{min:3,max:5,message:"长度在 3 到 5 个字符",trigger:"blur"}],staff_phone:[{required:!0,pattern:/^(13[0-9]|14[5|7]|15[0|1|2|3|5|6|7|8|9]|18[0|1|2|3|5|6|7|8|9])\d{8}$/,message:"手机号未填或格式不正确",trigger:"blur"}],staff_password:[{required:!0,pattern:/^(\w){6,20}$/,message:"请输入6-20个字母、数字、下划线",trigger:"blur"}]}}},methods:{submitForm:function(e){var t=this;this.$refs[e].validate(function(e){if(!e)return!1;t.AdialogFormVisible=!1,t.ruleForm.user_id=t.userInfo.user_id,i.a.managercreatestaff(t.ruleForm).then(function(e){200==result.data.code[0]?(t.$message.success(result.data.message[0]),t.Fncompanystaff()):t.$message.console.error(result.data.message[0])})})},Fncompanystaff:function(){var e=this;i.a.companystaff({company_id:this.userInfo.u_company_id,user_id:this.userInfo.user_id}).then(function(t){if(200==t.data.code[0]){var a=[];t.data.data.forEach(function(e){e.fields.user_id=e.pk,a.push(e.fields)}),e.tableDatareRE=a}})},Fnunactivestafflist:function(){var e=this;this.dialogFormVisible=!0,i.a.unactivestafflist({company_id:this.userInfo.u_company_id,user_id:this.userInfo.user_id}).then(function(t){var a=[];t.data.data.forEach(function(e){e.fields.user_id=e.pk,a.push(e.fields)}),e.ADDtableData=a})},Fnenrollstaff:function(e){var t=this;i.a.enrollstaff({user_id:e,user_id1:this.userInfo.user_id,company_id:this.userInfo.u_company_id}).then(function(e){t.Fnunactivestafflist(),t.Fncompanystaff()})},Fndeactivatestaff:function(e){var t=this;i.a.deactivatestaff({user_id:e,company_id:this.userInfo.u_company_id,user_id1:this.userInfo.user_id}).then(function(e){t.$message.success(e.data.message[0]),t.Fncompanystaff()})}},computed:r()({},Object(n.c)(["userInfo"])),mounted:function(){this.Fncompanystaff()}},o={render:function(){var e=this,t=e.$createElement,a=e._self._c||t;return a("div",[a("div",{staticClass:"title"},[e._v("\n        员工管理\n    ")]),e._v(" "),a("div",{staticClass:"relationBox_b"},[a("div",{staticClass:"jgTab"},[a("div",{staticClass:"tablebox"},[a("div",{staticClass:"jieGou_tit"},[e._v("\n              员工\n              "),a("div",{staticClass:"jieGou_tit_rigth"},[a("el-button",{attrs:{size:"small"},on:{click:e.Fnunactivestafflist}},[e._v("查看申请用户")]),e._v(" "),a("el-button",{attrs:{type:"primary",size:"small"},on:{click:function(t){e.AdialogFormVisible=!0}}},[e._v("新增用户")])],1),e._v(" "),a("el-divider")],1),e._v(" "),a("el-table",{staticStyle:{width:"100%"},attrs:{data:e.tableDatareRE,stripe:""}},[a("el-table-column",{attrs:{prop:"username",label:"用户名"}}),e._v(" "),a("el-table-column",{attrs:{prop:"phone_numbers",label:"手机"}}),e._v(" "),a("el-table-column",{attrs:{label:"操作",width:"180"},scopedSlots:e._u([{key:"default",fn:function(t){return[a("el-button",{attrs:{size:"small",type:"danger"},nativeOn:{click:function(a){return e.Fndeactivatestaff(t.row.user_id)}}},[e._v("停用")])]}}])})],1)],1)])]),e._v(" "),a("el-dialog",{attrs:{title:"申请列表",visible:e.dialogFormVisible},on:{"update:visible":function(t){e.dialogFormVisible=t}}},[a("el-table",{staticStyle:{width:"100%"},attrs:{data:e.ADDtableData,border:""}},[a("el-table-column",{attrs:{prop:"username",label:"用户名",width:"180"}}),e._v(" "),a("el-table-column",{attrs:{prop:"phone_numbers",label:"手机号"}}),e._v(" "),a("el-table-column",{attrs:{label:"操作",width:"120"},scopedSlots:e._u([{key:"default",fn:function(t){return[a("el-button",{attrs:{type:"success"},nativeOn:{click:function(a){return e.Fnenrollstaff(t.row.user_id)}}},[e._v("同意加入")])]}}])})],1)],1),e._v(" "),a("el-dialog",{attrs:{title:"新增员工",visible:e.AdialogFormVisible},on:{"update:visible":function(t){e.AdialogFormVisible=t}}},[a("el-form",{ref:"ruleForm",staticClass:"demo-ruleForm",attrs:{model:e.ruleForm,rules:e.rules,"label-width":"100px"}},[a("el-form-item",{attrs:{label:"用户名",prop:"staff_name"}},[a("el-input",{model:{value:e.ruleForm.staff_name,callback:function(t){e.$set(e.ruleForm,"staff_name",t)},expression:"ruleForm.staff_name"}})],1),e._v(" "),a("el-form-item",{attrs:{label:"手机号",prop:"staff_phone"}},[a("el-input",{model:{value:e.ruleForm.staff_phone,callback:function(t){e.$set(e.ruleForm,"staff_phone",t)},expression:"ruleForm.staff_phone"}})],1),e._v(" "),a("el-form-item",{attrs:{label:"密码",prop:"staff_password"}},[a("el-input",{model:{value:e.ruleForm.staff_password,callback:function(t){e.$set(e.ruleForm,"staff_password",t)},expression:"ruleForm.staff_password"}})],1),e._v(" "),a("el-form-item",[a("el-button",{attrs:{type:"primary"},on:{click:function(t){return e.submitForm("ruleForm")}}},[e._v("新增")])],1)],1)],1)],1)},staticRenderFns:[]};var u=a("VU/8")(l,o,!1,function(e){a("aerG")},"data-v-0245f118",null);t.default=u.exports},aerG:function(e,t){}});
//# sourceMappingURL=65.21a8425d6b9ab156ea5e.js.map