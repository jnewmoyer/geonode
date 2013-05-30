{% include 'geonode/ext_header.html' %}
{% include 'geonode/geo_header.html' %}
<style type="text/css">
#paneltbar {
    margin-top: 90px;
}
.map-title-header {
    margin-right: 10px;
}
</style>
<link rel="stylesheet" type="text/css" href="{{ STATIC_URL }}geonode/css/gbweb.css" />
<script type="text/javascript" src="{{ STATIC_URL}}geonode/js/maps/GeoBriefer.js"></script>
<script type="text/javascript">
var app;
Ext.onReady(function() {
{% autoescape off %}
    var config = Ext.apply({
        authStatus: {% if user.is_authenticated %} 200{% else %} 401{% endif %},
        proxy: "/proxy/?url=",
        printService: "/proxy/?url={{GEOSERVER_BASE_URL}}pdf/",
        /* The URL to a REST map configuration service.  This service 
         * provides listing and, with an authenticated user, saving of 
         * maps on the server for sharing and editing.
         */
        rest: "{% url maps_browse %}",
        ajaxLoginUrl: "{% url account_ajax_login %}",
        homeUrl: "{% url home %}",
        localGeoServerBaseUrl: "{{ GEOSERVER_BASE_URL }}",
        localCSWBaseUrl: "{{ CATALOGUE_BASE_URL }}",
        csrfToken: "{{ csrf_token }}",
        tools: [{ptype: "gxp_getfeedfeatureinfo"}]
    }, {{ config }});
    app = new GeoBrieferViewer(config);
{% endautoescape %}
});
</script>
