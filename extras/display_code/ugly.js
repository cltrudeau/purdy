// ------------------------------------------------------------------------
// --- VUE Configuration
Vue.prototype.window_portal = window;
Vue.component('treeselect', VueTreeselect.Treeselect);
var vm = new Vue({
    el: '#vue-container',
    delimiters:['[[', ']]'],
    data: {
        has_loaded: false,
        room_spec: undefined,
        showing_wall_index:0,
        all_selected: false,
        lib_tree_selected: null,
        lib_tree: [],
        editing_tile: null,
    },
    methods: {
        select_all: function() {
            vm.all_selected = true;
            for(var i=0; i<vm.showing_wall['tile_set'].length; i++) {
                Vue.set(vm.showing_wall['tile_set'][i], 'selected', 
                    true);
            }
        },
        change_title: (value)=>{
            vm.room_spec.name = value;
            send_room_spec();
        },
    },
});

// ------------------------------------------------------------------------
// ------------------------------------------------------------------------
// --- Event Management

function fetch_room_spec() {
    $.getJSON(FETCH_URL, function(response) {
        vm.room_spec = response;
        vm.has_loaded = true;

        Vue.nextTick(function() {
            $('[data-toggle="tooltip"]').tooltip();
            $('#sortable-tiles').sortable({
                handle:".tile-drag",
                update: function(event, ui) {
                    /* One of the tiles has had its order moved, this effects
                       its rank. */
                    var found = find_tile(ui.item[0].id);
                    $.ajax({
                        url:'/api/v1/change_tile_rank/' + tile.id +
                            '/' + new_rank + '/',
                        type:'GET',
                    });
                },
            });
        });
    }).fail(function() { // FETCH_URL fail
        console.log("JSON call fetching room_spec data failed");
    });
}


// ------------------------------------------------------------------------
// --- Utilities

function find_tile(slug) {
    var parts = slug.split('-');
    var tile_id = parseInt(parts[1]);
    var i, j;

    for(i=0; i<vm.room_spec.wall_set.length; i++) {
        var wall = vm.room_spec.wall_set[i];

        for(j=0; j<wall.tile_set.length; j++) {
            if(wall.tile_set[j]['id'] == tile_id) {
                // Found matching Tile, return describing object
                var response = {
                    wall:wall,
                    wall_index:i,
                    tile:wall.tile_set[j],
                    tile_index:j,
                };
                return response;
            }
        }
    }

    return '';
}

// ------------------------------------------------------------------------
// --- Document Ready
$(function() {
    fetch_room_spec();

    text_form = new RestModal('edit-text');

    create_lib_link = new FormModal('create-lib-link');
    $('#create-lib-link-select').click( ()=> {
        var parts = vm.lib_tree_selected.split('-');
        var lib_item_id = parseInt(parts[1]);

        var data = {
            is_visible:true,
            wall:vm.showing_wall.id,
            tile_type:'C',
            library_item:lib_item_id,
            title:$('#create-lib-tile-title').val(),
            description:$('#create-lib-tile-desc').val(),
        }
        $.ajax({
            url:'/api/v1/tiles/', 
            data:data,
            type:'POST',
            success:()=>{
                // New tile created, fetch data
                fetch_room_spec();
                Vue.nextTick(function() {
                    // Tiles haven't fully rendered yet, scroll to bottom plus
                    // a guess on what a big tile is, hackish but good enough
                    window.scrollTo(0, document.body.scrollHeight + 1000);
                });
            },
        });
    });
});
