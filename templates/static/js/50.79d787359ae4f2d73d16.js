webpackJsonp([50],{WJcD:function(t,e,i){"use strict";Object.defineProperty(e,"__esModule",{value:!0});var n=i("Dd8w"),o=i.n(n),s=i("sYY+"),a=i.n(s),r=i("w7XY"),c=i("NYxO"),d={data:function(){return{activeName:"first",editorContent:"",editor:null,input:"",region:""}},mounted:function(){var t=this;this.editor=new a.a(this.$refs.editor),this.editor.customConfig.onchange=function(e,i){t.editorContent=e},this.editor.customConfig.uploadImgServer=this.uploadimage,this.editor.customConfig.uploadFileName="image",this.editor.customConfig.uploadImgHooks={customInsert:function(t,e,i){t(e.ip+e.data[0])}},this.editor.customConfig.showLinkImg=!1,this.editor.create()},methods:{handleClick:function(t,e){},getContent:function(){var t=this;""!=this.input&&""!=this.editorContent&&""!=this.region?r.a.addknowledge({user_id:this.buserInfo.user_id,k_title:this.input,k_type:"知识库",k_content:this.editorContent,k_tag:this.region}).then(function(e){e.data.code&&(t.$message.success(e.data.message[0]),t.$router.push("/bkIndex/bkknowledge"))}):this.$message.error("标题、主题以及问题内容不能为空")}},computed:o()({},Object(c.c)(["static","uploadimage","tagList","buserInfo"]))},l={render:function(){var t=this,e=t.$createElement,i=t._self._c||e;return i("div",[i("div",{staticClass:"title"},[t._v("\n    问题描述\n  ")]),t._v(" "),i("div",{staticClass:"WOBox"},[i("div",{staticClass:"info"},[i("el-select",{staticClass:"Zinde",attrs:{placeholder:"请选择主题"},model:{value:t.region,callback:function(e){t.region=e},expression:"region"}},t._l(t.tagList,function(t,e){return i("el-option",{key:e,attrs:{label:t,value:t}})}),1)],1),t._v(" "),i("div",{staticClass:"textBox"},[t._v("\n      标题："),i("el-input",{staticClass:"inp",attrs:{placeholder:"请输入内容",maxlength:"32"},model:{value:t.input,callback:function(e){t.input=e},expression:"input"}}),t._v(" "),i("div",{ref:"editor",staticStyle:{"text-align":"left",position:"relative","z-index":"9"}})],1),t._v(" "),i("el-button",{attrs:{type:"primary"},on:{click:t.getContent}},[t._v("保存")])],1)])},staticRenderFns:[]};var u=i("VU/8")(d,l,!1,function(t){i("oYjy")},"data-v-381c5e8c",null);e.default=u.exports},oYjy:function(t,e){}});
//# sourceMappingURL=50.79d787359ae4f2d73d16.js.map