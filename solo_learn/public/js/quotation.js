frappe.ui.form.on('Quotation',{
    refresh: function(frm){
        frm.add_custom_button(('Do Something'),function(frm){
            let d = new frappe.ui.Dialog({
                    title: 'Enter details',
                    fields: [
                        {
                            label: 'First Name',
                            fieldname: 'first_name',
                            fieldtype: 'Data',
                        },
                        {
                            label: 'Last Name',
                            fieldname: 'last_name',
                            fieldtype: 'Data'
                        },
                    ],
                    primary_action_label: 'Create Sales Order',
                    primary_action(values) {
                        frappe.call({
                            method: "solo_learn.crud_events.test",
                            args:{
                                'doc': values.last_name
                            },
                            callback: function(r){
                                console.log(r.message);
                                let x = frm.add_child('items');
                                x.item_code = 'h';
                            }
                        });frm.refresh_fields("items");
                        console.log(values.age);
                        d.hide();
                    }
                });
                
                d.show();
        });
    }
});