webpackJsonp([9],{FzDR:function(e,t){},qSdn:function(e,t,s){"use strict";Object.defineProperty(t,"__esModule",{value:!0});var a=s("Dd8w"),n=s.n(a),i=s("NYxO"),l={data:function(){return{defaultActive:sessionStorage.getItem("defaultActive")||"1",ISdisabled:!0}},methods:n()({},Object(i.b)(["DelABuserInfo"]),{handleCommand:function(e){"e"==e&&(this.DelABuserInfo(),this.$router.push("/bklogin"))},handleSelect:function(e,t){switch(sessionStorage.setItem("defaultActive",e),this.defaultActive=sessionStorage.getItem("defaultActive"),e){case"1":this.$router.push("/bkIndex/bkkeHu");break;case"2":this.$router.push("/bkIndex/bkworkOrder");break;case"3":this.$router.push("/bkIndex/bkuserManagement");break;case"4":this.$router.push("/bkIndex/bkcomplaintAndSolve");break;case"5":this.$router.push("/bkIndex/bkknowledge");break;case"6":this.$router.push("/bkIndex/bknews");break;case"7":this.$router.push("/bkIndex/companylist");break;case"8":this.$router.push("/bkIndex/dynamicB");break;default:this.$router.push("/bkIndex/bkkeHu")}},Fndisabled:function(){"超级管理员"==this.buserInfo.u_type?this.ISdisabled=!1:"运维"==this.buserInfo.u_type?this.ISdisabled=!1:this.ISdisabled=!0}}),beforeRouteEnter:function(e,t,s){"L成功"!=sessionStorage.getItem("bkL")?s("/bklogin"):s()},computed:n()({},Object(i.c)(["buserInfo"])),mounted:function(){this.Fndisabled()}},o={render:function(){var e=this,t=e.$createElement,a=e._self._c||t;return a("div",{staticClass:"whole"},[a("el-container",{staticClass:"wholeBox"},[a("el-header",{staticClass:"headerBox"},[a("div",{staticClass:"hdB_left"},[a("img",{attrs:{src:s("sHGO"),alt:""}})]),e._v(" "),a("div",{staticClass:"hdB_rigth"},[a("el-dropdown",{on:{command:e.handleCommand}},[a("span",{staticClass:"el-dropdown-link"},[e._v("\n                  "+e._s(e.buserInfo.username)),a("i",{staticClass:"el-icon-arrow-down el-icon--right"})]),e._v(" "),a("el-dropdown-menu",{attrs:{slot:"dropdown"},slot:"dropdown"},[a("el-dropdown-item",{attrs:{command:"e"}},[e._v("退出")])],1)],1)],1)]),e._v(" "),a("el-main",{staticClass:"Main"},[a("el-menu",{staticClass:"el-menu-vertical-demo",attrs:{"default-active":e.defaultActive},on:{select:e.handleSelect}},[a("el-menu-item",{attrs:{index:"1"}},[a("span",{attrs:{slot:"title"},slot:"title"},[e._v("客户管理")])]),e._v(" "),a("el-menu-item",{attrs:{index:"3",disabled:!e.buserInfo.is_superuser}},[a("span",{attrs:{slot:"title"},slot:"title"},[e._v("员工管理")])]),e._v(" "),a("el-menu-item",{attrs:{index:"5"}},[a("span",{attrs:{slot:"title"},slot:"title"},[e._v("更新知识库")])]),e._v(" "),a("el-menu-item",{attrs:{index:"6"}},[a("span",{attrs:{slot:"title"},slot:"title"},[e._v("更新行业资讯")])]),e._v(" "),a("el-menu-item",{attrs:{index:"8",disabled:e.ISdisabled}},[a("span",{attrs:{slot:"title"},slot:"title"},[e._v("更新企业动态")])]),e._v(" "),a("el-menu-item",{attrs:{index:"7"}},[a("span",{attrs:{slot:"title"},slot:"title"},[e._v("注册公司列表")])])],1),e._v(" "),a("div",{staticClass:"rigthBox"},[a("router-view")],1)],1)],1)],1)},staticRenderFns:[]};var r=s("VU/8")(l,o,!1,function(e){s("FzDR")},"data-v-1efba52f",null);t.default=r.exports},sHGO:function(e,t,s){e.exports=s.p+"static/img/loginZ.45cbc55.jpg"}});
//# sourceMappingURL=9.8e2068063bff96fe88d0.js.map