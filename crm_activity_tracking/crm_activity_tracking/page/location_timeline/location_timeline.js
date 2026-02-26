frappe.pages['location-timeline'].on_page_load = function (wrapper) {

    let page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Employee Location Timeline',
        single_column: true
    });

    // Inject Professional Styling
    injectStyles();

    // -----------------------------
    // Add Filters (Frappe Native)
    // -----------------------------

    let employee_field = page.add_field({
        label: 'Employee',
        fieldtype: 'Link',
        fieldname: 'employee',
        options: 'Employee',
        reqd: 1,
        get_query: function () {
            return {
                filters: {
                    status: "Active"
                }
            };
        }
    });

    let date_field = page.add_field({
        label: 'Date',
        fieldtype: 'Date',
        fieldname: 'date',
        reqd: 1,
        default: frappe.datetime.get_today()
    });

    let button = page.add_field({
        label: 'Show Route',
        fieldtype: 'Button',
        fieldname: 'show_route'
    });

    // -----------------------------
    // Main Container
    // -----------------------------

    $(page.body).append(`
        <div class="timeline-card">
            <div id="alertBox" class="timeline-alert"></div>
            <div id="map"></div>
        </div>
    `);

    // Button Click
    button.$input.addClass("btn-primary");
    button.$input.on("click", function () {
        loadMapData(employee_field.get_value(), date_field.get_value());
    });
};



// ======================================
// STYLES
// ======================================

function injectStyles() {

    if ($("#timelineStyles").length) return;

    $("head").append(`
        <style id="timelineStyles">

            .timeline-card {
                background: #ffffff;
                border-radius: 12px;
                padding: 20px;
                margin-top: 20px;
                box-shadow: 0 6px 18px rgba(0,0,0,0.08);
            }

            #map {
                height: 600px;
                border-radius: 12px;
                margin-top: 15px;
            }

            .timeline-alert {
                display: none;
                padding: 12px;
                border-radius: 8px;
                background: #fff3cd;
                color: #856404;
                font-weight: 500;
                margin-bottom: 10px;
            }

        </style>
    `);
}



// ======================================
// GLOBAL VARIABLES
// ======================================

let map;
let markers = [];
let routeLine;



// ======================================
// ALERT HANDLING
// ======================================

function showAlert(message) {
    $("#map").hide();
    $("#alertBox").text(message).fadeIn();
}

function clearAlert() {
    $("#alertBox").hide().text("");
    $("#map").show();
}



// ======================================
// LOAD MAP DATA
// ======================================

function loadMapData(employee, date) {

    clearAlert();

    if (!employee) {
        showAlert("Please select an employee.");
        return;
    }

    if (!date) {
        showAlert("Please select a date.");
        return;
    }

    frappe.call({
        method: "crm_activity_tracking.crm_activity_tracking.utils.install.get_location_timeline",
        args: {
            employee: employee,
            date: date
        },
        callback: function (r) {

            if (!r.message || r.message.length === 0) {
                showAlert("No location history found for selected date.");
                return;
            }

            drawMap(r.message);
        }
    });
}



// ======================================
// DRAW MAP
// ======================================

function drawMap(points) {

    if (!points || points.length === 0) return;

    clearMap();

    let first = points[0];

    if (!map) {
        map = L.map('map').setView([first.latitude, first.longitude], 14);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap'
        }).addTo(map);
    }

    let latLngs = [];
    let groupedPoints = {};

    points.forEach(p => {

        let lat = roundCoord(p.latitude);
        let lng = roundCoord(p.longitude);

        let key = `${lat}_${lng}`;

        if (!groupedPoints[key]) groupedPoints[key] = [];
        groupedPoints[key].push(p);
    });

    Object.values(groupedPoints).forEach(group => {

        let lat = group[0].latitude;
        let lng = group[0].longitude;

        let marker = L.circleMarker([lat, lng], {
            radius: 7,
            color: '#2c7be5',
            fillColor: '#2c7be5',
            fillOpacity: 0.9
        }).addTo(map);

        let popup = `
            <div style="font-size:13px">
                <b>Location Logs</b><br><br>
                <b>Latitude:</b> ${lat}<br>
                <b>Longitude:</b> ${lng}<br><br>
                <b>Times:</b><br>
                ${group.map(g => `• ${g.time}`).join("<br>")}
            </div>
        `;

        marker.bindPopup(popup);

        markers.push(marker);
        latLngs.push([lat, lng]);
    });

    // Draw Route Line
    routeLine = L.polyline(latLngs, {
        color: '#2c7be5',
        weight: 3,
        opacity: 0.7
    }).addTo(map);

    map.fitBounds(latLngs);
}



// ======================================
// CLEAR MAP
// ======================================

function clearMap() {

    if (!map) return;

    markers.forEach(m => map.removeLayer(m));
    markers = [];

    if (routeLine) {
        map.removeLayer(routeLine);
        routeLine = null;
    }
}



// ======================================
// UTIL
// ======================================

function roundCoord(value, precision = 4) {
    return Number(value).toFixed(precision);
}
