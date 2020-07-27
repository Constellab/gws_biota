/**
 * LICENSE
 * This software is the exclusive property of Gencovery SAS. 
 * The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
 * About us: https://gencovery.com
 */

if( window.gws == undefined )
    window.gws = {}


function load_tables() {
//var explorerTab = window.gws.dashboard.getTabByName("explorer")
//explorerTab.load("/biota/tables")
console.log("CLIC !")
}

window.gws.biota = function(){
    load_tables()
    var explorerTab = window.gws.dashboard.getTabByName("explorer")
    var viewerTab = window.gws.dashboard.getTabByName("viewer")
    //explorerTab.load("/biota/home")
    explorerTab.load("/biota/tables")
    viewerTab.load("/biota/testviews")
}

window.gws.tables = function(){
    var explorerTab = window.gws.dashboard.getTabByName("explorer")
    explorerTab.load("/biota/tables")
}

window.gws.testviews = function(){
    var viewerTab = window.gws.dashboard.getTabByName("viewer")
    viewerTab.load("/biota/testviews")
}
