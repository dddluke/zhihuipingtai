webpackJsonp([44],{"83LC":function(t,e,d){"use strict";Object.defineProperty(e,"__esModule",{value:!0});var n=d("w7XY"),i={data:function(){return{det:{},solution:{},ISsolution:!1}},methods:{Fneditknowledge:function(){var t=this;"行业资讯"==this.$route.query.k_type?n.a.editknowledge({k_id:this.$route.query.k_id}).then(function(e){if(e.data.code[0]="200"){var d=e.data.data[0].fields;d.k_id=e.data.data[0].pk,t.det=d}}):n.a.viewenterprise({k_id:this.$route.query.k_id}).then(function(e){if(e.data.code[0]="200"){var d=e.data.data[0].fields;d.k_id=e.data.data[0].pk,t.det.k_id=d.k_id,t.det.k_title=d.e_title,t.det.k_user_name=d.e_user_name,t.det.k_date=d.e_date,t.$set(t.det,"k_content",d.e_content)}})}},mounted:function(){this.Fneditknowledge()}},a={render:function(){var t=this,e=t.$createElement,d=t._self._c||e;return d("div",{staticClass:"DetailBox"},[d("h1",{staticClass:"detTitle"},[t._v(t._s(t.det.k_title))]),t._v(" "),d("div",{staticClass:"infod"},[t._v("\n        写作人"),d("i",[t._v(t._s(t.det.k_user_name))]),t._v(t._s(t._f("toTime")(t.det.k_date))+"\n    ")]),t._v(" "),d("div",{staticClass:"DetTontent",domProps:{innerHTML:t._s(t.det.k_content)}})])},staticRenderFns:[]};var s=d("VU/8")(i,a,!1,function(t){d("BSfY")},"data-v-44f53380",null);e.default=s.exports},BSfY:function(t,e){}});
//# sourceMappingURL=44.f5115ce7b40837bdef54.js.map