webpackJsonp([67],{ZUD9:function(t,a){},qthT:function(t,a,e){"use strict";Object.defineProperty(a,"__esModule",{value:!0});var s=e("w7XY"),n={data:function(){return{dashboard:""}},methods:{Fndashboardv2:function(){var t=this;s.a.dashboardv2({id:this.$route.query.id}).then(function(a){t.dashboard=a.data.dashboardurl,(a.data.code[0]="200")?t.$message({message:a.data.message[0],type:"success"}):t.$message({message:a.data.message[0],type:"warning"})})}},mounted:function(){this.Fndashboardv2()}},d={render:function(){var t=this.$createElement,a=this._self._c||t;return a("div",[a("div",{staticClass:"title"},[this._v("\n      组态图\n  ")]),this._v(" "),a("iframe",{attrs:{src:this.dashboard,frameborder:"0",scrolling:"no",width:"1200",height:"750"}})])},staticRenderFns:[]};var r=e("VU/8")(n,d,!1,function(t){e("ZUD9")},"data-v-003191f4",null);a.default=r.exports}});
//# sourceMappingURL=67.22288abd7fb86655d745.js.map