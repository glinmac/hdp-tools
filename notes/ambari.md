# Ambari Notes

## Upgrade
When upgrading from 2.1 to 2.4.1.0, the database upgrade seemed to complain about object not being owned by the correct user:

    Exception in thread "main" org.apache.ambari.server.AmbariException: ERROR: must be owner of relation topology_request


To fix it:

    ALTER TABLE adminpermission OWNER TO ambari;
    ALTER TABLE adminprincipal OWNER TO ambari;
    ALTER TABLE adminprincipaltype OWNER TO ambari;
    ALTER TABLE adminprivilege OWNER TO ambari;
    ALTER TABLE adminresource OWNER TO ambari;
    ALTER TABLE adminresourcetype OWNER TO ambari;
    ALTER TABLE alert_current OWNER TO ambari;
    ALTER TABLE alert_definition OWNER TO ambari;
    ALTER TABLE alert_group OWNER TO ambari;
    ALTER TABLE alert_group_target OWNER TO ambari;
    ALTER TABLE alert_grouping OWNER TO ambari;
    ALTER TABLE alert_history OWNER TO ambari;
    ALTER TABLE alert_notice OWNER TO ambari;
    ALTER TABLE alert_target OWNER TO ambari;
    ALTER TABLE alert_target_states OWNER TO ambari;
    ALTER TABLE ambari_sequences OWNER TO ambari;
    ALTER TABLE artifact OWNER TO ambari;
    ALTER TABLE blueprint OWNER TO ambari;
    ALTER TABLE blueprint_configuration OWNER TO ambari;
    ALTER TABLE cluster_version OWNER TO ambari;
    ALTER TABLE clusterconfig OWNER TO ambari;
    ALTER TABLE clusterconfigmapping OWNER TO ambari;
    ALTER TABLE clusterhostmapping OWNER TO ambari;
    ALTER TABLE clusters OWNER TO ambari;
    ALTER TABLE clusterservices OWNER TO ambari;
    ALTER TABLE clusterstate OWNER TO ambari;
    ALTER TABLE confgroupclusterconfigmapping OWNER TO ambari;
    ALTER TABLE configgroup OWNER TO ambari;
    ALTER TABLE configgrouphostmapping OWNER TO ambari;
    ALTER TABLE execution_command OWNER TO ambari;
    ALTER TABLE groups OWNER TO ambari;
    ALTER TABLE host_role_command OWNER TO ambari;
    ALTER TABLE host_version OWNER TO ambari;
    ALTER TABLE hostcomponentdesiredstate OWNER TO ambari;
    ALTER TABLE hostcomponentstate OWNER TO ambari;
    ALTER TABLE hostconfigmapping OWNER TO ambari;
    ALTER TABLE hostgroup OWNER TO ambari;
    ALTER TABLE hostgroup_component OWNER TO ambari;
    ALTER TABLE hostgroup_configuration OWNER TO ambari;
    ALTER TABLE hosts OWNER TO ambari;
    ALTER TABLE hoststate OWNER TO ambari;
    ALTER TABLE kerberos_principal OWNER TO ambari;
    ALTER TABLE kerberos_principal_host OWNER TO ambari;
    ALTER TABLE key_value_store OWNER TO ambari;
    ALTER TABLE members OWNER TO ambari;
    ALTER TABLE metainfo OWNER TO ambari;
    ALTER TABLE qrtz_blob_triggers OWNER TO ambari;
    ALTER TABLE qrtz_calendars OWNER TO ambari;
    ALTER TABLE qrtz_cron_triggers OWNER TO ambari;
    ALTER TABLE qrtz_fired_triggers OWNER TO ambari;
    ALTER TABLE qrtz_job_details OWNER TO ambari;
    ALTER TABLE qrtz_locks OWNER TO ambari;
    ALTER TABLE qrtz_paused_trigger_grps OWNER TO ambari;
    ALTER TABLE qrtz_scheduler_state OWNER TO ambari;
    ALTER TABLE qrtz_simple_triggers OWNER TO ambari;
    ALTER TABLE qrtz_simprop_triggers OWNER TO ambari;
    ALTER TABLE qrtz_triggers OWNER TO ambari;
    ALTER TABLE repo_version OWNER TO ambari;
    ALTER TABLE request OWNER TO ambari;
    ALTER TABLE requestoperationlevel OWNER TO ambari;
    ALTER TABLE requestresourcefilter OWNER TO ambari;
    ALTER TABLE requestschedule OWNER TO ambari;
    ALTER TABLE requestschedulebatchrequest OWNER TO ambari;
    ALTER TABLE role_success_criteria OWNER TO ambari;
    ALTER TABLE servicecomponentdesiredstate OWNER TO ambari;
    ALTER TABLE serviceconfig OWNER TO ambari;
    ALTER TABLE serviceconfighosts OWNER TO ambari;
    ALTER TABLE serviceconfigmapping OWNER TO ambari;
    ALTER TABLE servicedesiredstate OWNER TO ambari;
    ALTER TABLE stack OWNER TO ambari;
    ALTER TABLE stage OWNER TO ambari;
    ALTER TABLE topology_host_info OWNER TO ambari;
    ALTER TABLE topology_host_request OWNER TO ambari;
    ALTER TABLE topology_host_task OWNER TO ambari;
    ALTER TABLE topology_hostgroup OWNER TO ambari;
    ALTER TABLE topology_logical_request OWNER TO ambari;
    ALTER TABLE topology_logical_task OWNER TO ambari;
    ALTER TABLE topology_request OWNER TO ambari;
    ALTER TABLE upgrade OWNER TO ambari;
    ALTER TABLE upgrade_group OWNER TO ambari;
    ALTER TABLE upgrade_item OWNER TO ambari;
    ALTER TABLE users OWNER TO ambari;
    ALTER TABLE viewentity OWNER TO ambari;
    ALTER TABLE viewinstance OWNER TO ambari;
    ALTER TABLE viewinstancedata OWNER TO ambari;
    ALTER TABLE viewinstanceproperty OWNER TO ambari;
    ALTER TABLE viewmain OWNER TO ambari;
    ALTER TABLE viewparameter OWNER TO ambari;
    ALTER TABLE viewresource OWNER TO ambari;
    ALTER TABLE widget OWNER TO ambari;
    ALTER TABLE widget_layout OWNER TO ambari;
    ALTER TABLE widget_layout_user_widget OWNER TO ambari;


## Ambari agents

It's possible to control which hostname the agents registered to the Ambari Server:

 * [How to customize the name of a host](http://docs.hortonworks.com/HDPDocuments/Ambari-2.1.2.0/bk_ambari_reference_guide/content/_how_to_customize_the_name_of_a_host.html)

## LDAP

  * [Automate LDAP sync](https://community.hortonworks.com/questions/2909/how-do-i-automate-the-ambari-ldap-sync.html)

## Privileges / permissions

  * Adding privileges
  
        curl -u admin:admin \
	          -H "X-Requested-By:ambari" \
	          -i -X POST \
	          -d '[{"PrivilegeInfo":{"permission_name":"CLUSTER.READ", "principal_name":"ambari_admin_group", "principal_type":"GROUP"} } ]'  \
	          http://localhost:8080/api/v1/clusters/my_cluster/privileges

## Widgets

This can be achieved using the widget editor in the UI or also could be automated using the Ambari API.

### Create

Widgets are defined in JSON, for instance for details about the NameNode heap:

    {  
      "WidgetInfo" : {
        "author" : "admin",
        "cluster_name" : "hadoop_cluster",
        "widget_name" : "NameNode Heap (COPY of Existing)",
        "description" : "Heap memory committed and Heap memory used with respect to time.",    
        "metrics" : [{"service_name":"HDFS","component_name":"NAMENODE","name":"jvm.JvmMetrics.MemHeapUsedM._avg","metric_path":"metrics/jvm/memHeapUsedM._avg"},{"service_name":"HDFS","component_name":"NAMENODE","name":"jvm.JvmMetrics.MemHeapCommittedM._avg","metric_path":"metrics/jvm/memHeapCommittedM._avg"}],
        "properties" : {"graph_type":"LINE","display_unit":"MB"},
        "scope" : "USER",    
        "values" : [{"name":"jvm.JvmMetrics.MemHeapUsedM","value":"${jvm.JvmMetrics.MemHeapUsedM._avg}"},{"name":"jvm.JvmMetrics.MemHeapCommittedM","value":"${jvm.JvmMetrics.MemHeapCommittedM._avg}"}],
        "widget_type" : "GRAPH"
      }
    }
    
This can be sent to the widget endpoint:
    
    $ curl -u admin:admin -H 'X-Requested-By: ambari' -i \
       -X POST \
       -d @widget.json
       http://localhost:8080/api/v1/clusters/hadoop_cluster/widgets
    
    HTTP/1.1 201 Created
    ...
    {
      "resources" : [
        {
          "href" : "http://localhost:8080/api/v1/clusters/hadoop_cluster/widgets/252",
          "WidgetInfo" : {
            "id" : 252
          }
        }
      ]
    }

### Retrieve / Get

You can then check that it is defined: 

* All widgets: http://localhost:8080/api/v1/clusters/hadoop_cluster/widgets
* Widget just created: http://localhost:8080/api/v1/clusters/hadoop_cluster/widgets/252
    
### Update

Same process than creation but with a PUT request with the new widget definition:

    $ curl -u admin:admin -H 'X-Requested-By: ambari' -i \
           -X PUT \
           -d @widget.json
           http://localhost:8080/api/v1/clusters/hadoop_cluster/widgets/252

### Delete

This can be deleted by sending a DELETE request:

    $ curl -u admin:admin -H 'X-Requested-By: ambari' -i \
           -X DELETE \
           http://localhost:8080/api/v1/clusters/hadoop_cluster/widgets

### Mapping a widget to a widget layout

User can map manually widget to their prefered dashboard or this could also be automated so that it is available by default.

The following gives the list of layouts available:

    $ curl -u admin:admin -H 'X-Requested-By: ambari' -i  \
        http://localhost:8080/api/v1/clusters/hadoop_cluster/widget_layouts
    HTTP/1.1 200 OK
    ...
    {
      "href" : "http://localhost:8080/api/v1/clusters/hadoop_cluster/widget_layouts",
      "items" : [
        {
          "href" : "http://localhost:8080/api/v1/clusters/hadoop_cluster/widget_layouts/8",
          "WidgetLayoutInfo" : {
            "cluster_name" : "hadoop_cluster",
            "display_name" : "Standard HDFS Dashboard",
            "id" : 8,
            "layout_name" : "admin_hdfs_dashboard",
            "scope" : "USER",
            "section_name" : "HDFS_SUMMARY",
            "user_name" : "admin",
            "widgets" : [
              {
                "href" : "http://localhost:8080/api/v1/clusters/hadoop_cluster/widgets/20",
                "WidgetInfo" : {
                  "id" : 20,
    ...
    
You can also use a filter to look for a specific widget given one of its property:

    $ curl -u admin:admin -H 'X-Requested-By: ambari' -i  \
        http://localhost:8080/api/v1/clusters/hadoop_cluster/widget_layouts?WidgetLayoutInfo/layout_name=admin_hdfs_dashboard

To add a widget to a given layout, this is a matter of updating the list of widget IDs associated with the widget layout.

The data to update:

    {
      "WidgetLayoutInfo":
    	{
    		"display_name":"Standard HDFS Dashboard",
    		"id":8,
    		"layout_name":"admin_hdfs_dashboard",
    		"scope":"USER",
    		"section_name":"HDFS_SUMMARY",
    		"widgets":
    			[{"id":20},{"id":23},{"id":22},{"id":24},{"id":21},{"id":153},{"id":152},{"id":25},{"id":26},{"id":27},{"id":28},{"id":29},{"id":252}]
    	}
    }

The update request:

    $ curl -u admin:admin -H 'X-Requested-By: ambari' -i  \
        -X PUT \
        -d @widget_layout.json \
        http://localhost:8080/api/v1/clusters/hadoop_cluster/widget_layouts/8
