webpackJsonp([19],{ih6a:function(a,t){},t57s:function(a,t,e){"use strict";Object.defineProperty(t,"__esModule",{value:!0});var s=e("w7XY"),n={data:function(){return{dashboard:""}},methods:{Fndashboardv2:function(){var a=this;s.a.dashboardv2({id:this.$route.query.id}).then(function(t){a.dashboard=t.data.dashboardurl,(t.data.code[0]="200")?a.$message({message:t.data.message[0],type:"success"}):a.$message({message:t.data.message[0],type:"warning"})})}},mounted:function(){this.Fndashboardv2()}},d={render:function(){var a=this.$createElement,t=this._self._c||a;return t("div",[t("div",{staticClass:"title"},[this._v("\n      组态图\n  ")]),this._v(" "),t("iframe",{attrs:{src:this.dashboard,frameborder:"0",scrolling:"no",width:"1200",height:"750"}})])},staticRenderFns:[]};var r=e("VU/8")(n,d,!1,function(a){e("ih6a")},"data-v-c3f62f54",null);t.default=r.exports}});
//# sourceMappingURL=19.b39e8dd7893ee6132b70.js.map