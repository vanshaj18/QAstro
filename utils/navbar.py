import pages as pg
navbar = """
<style> 
        .navbar-container {
            position: relative;
            width: 100%;
            background-color: #0A5B99;
            # padding: 1rem 2rem;
            overflow: hidden;
            border-radius: 5px;
            font-size: 1.5em;
            font-family: "Times New Roman", serif;
            text-align: center;
        }
        .navbar-overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 1;
        }
        .navbar-content {
            position: relative;
            z-index: 2;
            display: flex;
            gap: 5rem;
            justify-content: space-between;
        }
        .nav-column {
            display: flex;
            flex-direction: row;
            gap: 0.5rem;
        }
        .nav-item {
            padding: 0.5rem 0;
            cursor: pointer;
            transition: color 0.3s ease;
        }
        .nav-item:hover {
            color: #00bcd4;
        }
        /* Customizable column count */
        .columns-2 {
            flex-direction: row;
        }

        .columns-3 .nav-column {
            width: 33.33%;
        }
        .columns-4 .nav-column {
            width: 25%;
        }
</style>"""
f"""
<div class="navbar-container">
    <div class="navbar-overlay"></div>
        <div class="navbar-content columns-2">
            <div class="nav-column">
                <div class="nav-item">{pg.home_page}</div>
                <div class="nav-item">{pg.data_page}</div>
            </div>
    </div>
</div>"""