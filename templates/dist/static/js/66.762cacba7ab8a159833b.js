webpackJsonp([66],{ERBK:function(e,r,t){"use strict";Object.defineProperty(r,"__esModule",{value:!0});var a=t("Dd8w"),o=t.n(a),l=t("w7XY"),i=t("NYxO"),s={data:function(){return{activeName:"first",value:!1,formLabelAlign:{cd_nodeid:"",cd_name:"",cd_produce_time:"",cd_manufacturer:""},rulesA:{cd_nodeid:[{required:!0,message:"请输入设备id",trigger:"blur"},{type:"number",message:"请输入数字",trigger:"blur"}],cd_name:[{required:!0,message:"请输入设备名称",trigger:"blur"}],cd_produce_time:[{required:!0,message:"请输入设备出场日期",trigger:"blur"}],cd_manufacturer:[{required:!0,message:"请输入设备生产商",trigger:"blur"}]},ISfromBox:!0,ruleForm:{p_name:"",p_dashboard:"",p_description:"",p_type:"",p_customer_type:"",p_party_a:"",p_purchase_time:"",p_setup_time:"",p_built_time:"",p_contact_name:"",p_contact_number:"",p_province:"",p_city:"",p_address:""},rules:{p_name:[{required:!0,message:"请输入项目名称",trigger:"blur"}],p_dashboard:[{required:!0,message:"请输入组态画面地址",trigger:"blur"},{type:"url",message:"请输入url地址",trigger:"blur"}],p_type:[{required:!0,message:"请输入项目类型",trigger:"blur"}],p_party_a:[{required:!0,message:"请输入甲方单位",trigger:"blur"}],p_province:[{required:!0,message:"请输入省份",trigger:"blur"}],p_city:[{required:!0,message:"请输入城市",trigger:"blur"}],p_address:[{required:!0,message:"请输入地址",trigger:"blur"}]}}},methods:{handleClick:function(e){"关联的员工"==e.label&&this.$router.push({path:"/bkIndex/bkseeProjectManagement/signproject",query:{company_id:this.$route.query.company_id,project_id:this.$route.query.project_id}})},onSubmit:function(){},submitForm:function(e){var r=this;this.$refs[e].validate(function(e){if(!e)return!1;r.formLabelAlign.company_id=r.$route.query.company_id,r.formLabelAlign.project_id=r.$route.query.project_id,r.formLabelAlign.user_id=r.buserInfo.user_id,r.ISfromBox?l.a.editcollectdevice(r.formLabelAlign).then(function(e){r.Fncollectdevicelist(),e.data.code?r.$message({message:e.data.message[0],type:"success"}):r.$message({message:"修改失败，请检查信息重新修改",type:"error"})}):l.a.applycollectdevice(r.formLabelAlign).then(function(e){r.Fncollectdevicelist(),e.data.code?r.$message({message:e.data.message[0],type:"success"}):r.$message({message:"添加失败，请检查信息重新修改",type:"error"})})})},Fndelcollectdevice:function(){var e=this;l.a.delcollectdevice({cdevice_id:this.formLabelAlign.cdevice_id,user_id:this.buserInfo.user_id}).then(function(r){e.Fncollectdevicelist(),r.data.code?e.$message({message:r.data.message[0],type:"success"}):e.$message({message:"删除失败，请检查信息重新修改",type:"error"})})},Fnhistory:function(e){},FnGonSubmit:function(){},Fnviewproject:function(){var e=this;l.a.viewproject({project_id:this.$route.query.project_id,company_id:this.$route.query.company_id,user_id:this.buserInfo.user_id}).then(function(r){if(r.data.code[0]="200"){var t=r.data.data[0].fields;t.project_id=r.data.data[0].pk,e.ruleForm=t}else e.$message.error("查看项目信息失败")})},Fneditproject:function(e){var r=this;this.$refs[e].validate(function(e){if(!e)return!1;r.ruleForm.company_id=r.$route.query.company_id,r.ruleForm.user_id=r.buserInfo.user_id,l.a.editproject(r.ruleForm).then(function(e){"200"==e.data.code[0]?r.$message.success(e.data.message[0]):r.$message.error("项目修改不成功，请重新创建")})})},Fndeactivateproject:function(){var e=this;l.a.deactivateproject({project_id:this.$route.query.project_id,company_id:this.$route.query.company_id,user_id:this.buserInfo.user_id}).then(function(r){"200"==r.data.code[0]?(e.$router.push("/bkIndex/bkprojectManagement"),e.$message.success("删除成功")):e.$message.error("删除项目不成功")})},Fncollectdevicelist:function(){var e=this;l.a.collectdevicelist({project_id:this.$route.query.project_id,user_id:this.buserInfo.user_id}).then(function(r){if(0==r.data.data.length)e.ISfromBox=!1,e.formLabelAlign={};else{e.ISfromBox=!0;var t=r.data.data[0].fields;t.cdevice_id=r.data.data[0].pk,e.formLabelAlign=t}})}},filters:{filters2:function(e){return e>=100?"99+":e}},computed:o()({},Object(i.c)(["buserInfo"])),mounted:function(){this.Fnviewproject(),this.Fncollectdevicelist()}},n={render:function(){var e=this,r=e.$createElement,t=e._self._c||r;return t("div",{staticStyle:{margin:"25px 30px","min-width":"1000px"}},[t("el-tabs",{attrs:{type:"card"},on:{"tab-click":e.handleClick},model:{value:e.activeName,callback:function(r){e.activeName=r},expression:"activeName"}},[t("el-tab-pane",{attrs:{label:"项目信息",name:"first"}},[t("el-form",{ref:"ruleForm",staticClass:"demo-ruleForm",attrs:{model:e.ruleForm,rules:e.rules,"label-width":"100px"}},[t("el-form-item",{attrs:{label:"项目名称",prop:"p_name"}},[t("el-input",{model:{value:e.ruleForm.p_name,callback:function(r){e.$set(e.ruleForm,"p_name",r)},expression:"ruleForm.p_name"}})],1),e._v(" "),t("el-form-item",{attrs:{label:"画面地址",prop:"p_dashboard"}},[t("el-input",{model:{value:e.ruleForm.p_dashboard,callback:function(r){e.$set(e.ruleForm,"p_dashboard",r)},expression:"ruleForm.p_dashboard"}})],1),e._v(" "),t("el-form-item",{attrs:{label:"省",prop:"p_province"}},[t("el-input",{model:{value:e.ruleForm.p_province,callback:function(r){e.$set(e.ruleForm,"p_province",r)},expression:"ruleForm.p_province"}})],1),e._v(" "),t("el-form-item",{attrs:{label:"市",prop:"p_city"}},[t("el-input",{model:{value:e.ruleForm.p_city,callback:function(r){e.$set(e.ruleForm,"p_city",r)},expression:"ruleForm.p_city"}})],1),e._v(" "),t("el-form-item",{attrs:{label:"甲方单位",prop:"p_party_a"}},[t("el-input",{model:{value:e.ruleForm.p_party_a,callback:function(r){e.$set(e.ruleForm,"p_party_a",r)},expression:"ruleForm.p_party_a"}})],1),e._v(" "),t("el-form-item",{attrs:{label:"采购日期",prop:"p_purchase_time"}},[t("el-date-picker",{attrs:{type:"date",format:"yyyy 年 MM 月 dd 日","value-format":"yyyy-MM-dd",placeholder:"选择日期"},model:{value:e.ruleForm.p_purchase_time,callback:function(r){e.$set(e.ruleForm,"p_purchase_time",r)},expression:"ruleForm.p_purchase_time"}})],1),e._v(" "),t("el-form-item",{attrs:{label:"竣工日期",prop:"p_built_time"}},[t("el-date-picker",{attrs:{type:"date",format:"yyyy 年 MM 月 dd 日","value-format":"yyyy-MM-dd",placeholder:"选择日期"},model:{value:e.ruleForm.p_built_time,callback:function(r){e.$set(e.ruleForm,"p_built_time",r)},expression:"ruleForm.p_built_time"}})],1),e._v(" "),t("el-form-item",{attrs:{label:"联系人姓名",prop:"p_contact_name"}},[t("el-input",{model:{value:e.ruleForm.p_contact_name,callback:function(r){e.$set(e.ruleForm,"p_contact_name",r)},expression:"ruleForm.p_contact_name"}})],1),e._v(" "),t("el-form-item",{attrs:{label:"联系人的电话",prop:"p_contact_number"}},[t("el-input",{model:{value:e.ruleForm.p_contact_number,callback:function(r){e.$set(e.ruleForm,"p_contact_number",r)},expression:"ruleForm.p_contact_number"}})],1),e._v(" "),t("el-form-item",{attrs:{label:"客户类型",prop:"p_customer_type"}},[t("el-input",{model:{value:e.ruleForm.p_customer_type,callback:function(r){e.$set(e.ruleForm,"p_customer_type",r)},expression:"ruleForm.p_customer_type"}})],1),e._v(" "),t("el-form-item",{attrs:{label:"项目类型",prop:"p_type"}},[t("el-input",{model:{value:e.ruleForm.p_type,callback:function(r){e.$set(e.ruleForm,"p_type",r)},expression:"ruleForm.p_type"}})],1),e._v(" "),t("el-form-item",{attrs:{label:"地址",prop:"p_address"}},[t("el-input",{model:{value:e.ruleForm.p_address,callback:function(r){e.$set(e.ruleForm,"p_address",r)},expression:"ruleForm.p_address"}})],1),e._v(" "),t("el-form-item",{attrs:{label:"安装时间",prop:"p_setup_time"}},[t("el-date-picker",{attrs:{type:"date",format:"yyyy 年 MM 月 dd 日","value-format":"yyyy-MM-dd",placeholder:"选择日期"},model:{value:e.ruleForm.p_setup_time,callback:function(r){e.$set(e.ruleForm,"p_setup_time",r)},expression:"ruleForm.p_setup_time"}})],1),e._v(" "),t("el-form-item",{attrs:{label:"项目简介",prop:"p_description"}},[t("el-input",{attrs:{type:"textarea"},model:{value:e.ruleForm.p_description,callback:function(r){e.$set(e.ruleForm,"p_description",r)},expression:"ruleForm.p_description"}})],1),e._v(" "),t("el-form-item",[t("el-button",{attrs:{type:"primary"},on:{click:function(r){return e.Fneditproject("ruleForm")}}},[e._v("修改")])],1)],1),e._v(" "),t("el-button",{attrs:{type:"danger"},on:{click:e.Fndeactivateproject}},[e._v("删除项目")])],1),e._v(" "),t("el-tab-pane",{attrs:{label:"画面",name:"second"}},[t("iframe",{attrs:{src:e.ruleForm.p_dashboard,frameborder:"0",scrolling:"no",width:"1200",height:"750"}})]),e._v(" "),t("el-tab-pane",{attrs:{label:"采集设备",name:"fourth"}},[t("div",{staticClass:"fromBox"},[t("el-form",{ref:"formLabelAlign",attrs:{"label-position":"right",rules:e.rulesA,"label-width":"100px",model:e.formLabelAlign}},[t("el-form-item",{attrs:{label:"采集设备id",prop:"cd_nodeid"}},[t("el-input",{model:{value:e.formLabelAlign.cd_nodeid,callback:function(r){e.$set(e.formLabelAlign,"cd_nodeid",e._n(r))},expression:"formLabelAlign.cd_nodeid"}})],1),e._v(" "),t("el-form-item",{attrs:{label:"设备名称",prop:"cd_name"}},[t("el-input",{model:{value:e.formLabelAlign.cd_name,callback:function(r){e.$set(e.formLabelAlign,"cd_name",r)},expression:"formLabelAlign.cd_name"}})],1),e._v(" "),t("el-form-item",{attrs:{label:"出场日期",prop:"cd_produce_time"}},[t("el-input",{model:{value:e.formLabelAlign.cd_produce_time,callback:function(r){e.$set(e.formLabelAlign,"cd_produce_time",r)},expression:"formLabelAlign.cd_produce_time"}})],1),e._v(" "),t("el-form-item",{attrs:{label:"设备生产商",prop:"cd_manufacturer"}},[t("el-input",{model:{value:e.formLabelAlign.cd_manufacturer,callback:function(r){e.$set(e.formLabelAlign,"cd_manufacturer",r)},expression:"formLabelAlign.cd_manufacturer"}})],1),e._v(" "),t("el-form-item",[t("el-button",{attrs:{type:"primary"},on:{click:function(r){return e.submitForm("formLabelAlign")}}},[e._v(e._s(e.ISfromBox?"修改":"添加"))]),e._v(" "),t("el-button",{directives:[{name:"show",rawName:"v-show",value:e.ISfromBox,expression:"ISfromBox"}],attrs:{type:"danger"},on:{click:function(r){return e.Fndelcollectdevice()}}},[e._v("删除")])],1)],1)],1)]),e._v(" "),t("el-tab-pane",{attrs:{label:"关联的员工",name:"shezhi"}},[t("router-view")],1)],1)],1)},staticRenderFns:[]};var c=t("VU/8")(s,n,!1,function(e){t("oWeR")},"data-v-01797863",null);r.default=c.exports},oWeR:function(e,r){}});
//# sourceMappingURL=66.762cacba7ab8a159833b.js.map