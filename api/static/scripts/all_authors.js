function page_ctrl(data_obj) {
    var obj_box = (data_obj.obj_box !== undefined) ? data_obj.obj_box : function () { return; }; //Page Dom Object
    var total_item = (data_obj.total_item !== undefined) ? parseInt(data_obj.total_item) : 0; //Total num of authors
    var per_num = (data_obj.per_num !== undefined) ? parseInt(data_obj.per_num) : 5; //Default num of authors per page
    var current_page = (data_obj.current_page !== undefined) ? parseInt(data_obj.current_page) : 1; //Current page
    var total_page = Math.ceil(total_item / per_num); //Compute the num of pages
    if (total_page < 2) { return; }

    // Adding the content
    $(obj_box).append('<div class="page_content"></div>');
    // Adding the page manage
    $(obj_box).append('<div class="page_ctrl"></div>');

    function page_even() {
        // Loding the data
        function change_content() {
            var page_content = '<ul style="width: 300px;margin: 10px auto;">';
            for (var i = 0; i < per_num; i++) {
                page_content += '<li>' + ((current_page - 1) * per_num + i + 1) + ',item</li>';
            }
            page_content += '</ul>';
            $(obj_box).children('.page_content').html(page_content);
        }

        change_content();

        var inp_val = (current_page == total_page) ? 1 : current_page + 1; //jump page
        var append_html = '<button class="prev_page">Previous Page</button>';

        for (var i = 0; i < total_page - 1; i++) {
            if (total_page > 8 && current_page > 6 && i < current_page - 3) {
                if (i < 2) {
                    append_html += '<button class="page_num">' + (i + 1) + '</button>';
                }
                else if (i == 2) {
                    append_html += '<span class="page_dot">~~~</span>';
                }
            }
            else if (total_page > 8 && current_page < total_page - 3 && i > current_page + 1) {
                if (current_page > 6 && i == current_page + 2) {
                    append_html += '<span class="page_dot">•••</span>';
                } else if (current_page < 7) {
                    if (i < 8) {
                        append_html += '<button class="page_num">' + (i + 1) + '</button>';
                    } else if (i == 8) {
                        append_html += '<span class="page_dot">•••</span>';
                    }
                }
            }
            else {
                if (i == current_page - 1) {
                    append_html += '<button class="page_num current_page">' + (i + 1) + '</button>';
                }
                else {
                    append_html += '<button class="page_num">' + (i + 1) + '</button>';
                }
            }
        }
        if (current_page == total_page) {
            append_html += '<button class="page_num current_page">' + (i + 1) + '</button>';
        } else {
            append_html += '<button class="page_num">' + (i + 1) + '</button>';
        }
        append_html += '<button class="next_page">Next Page</button><span class="page_total">Total ' + total_page 
        append_html += ' Page, To</span><input class="input_page_num" type="text" value="' + inp_val + '"><span class="page_text">Page</span><button class="to_page_num">Confirm</button>';
        $(obj_box).children('.page_ctrl').append(append_html);
        if (current_page == 1) {
            $(obj_box + ' .page_ctrl .prev_page').attr('disabled', 'disabled').addClass('btn_dis');
        } else {
            $(obj_box + ' .page_ctrl .prev_page').removeAttr('disabled').removeClass('btn_dis');
        }
        if (current_page == total_page) {
            $(obj_box + ' .page_ctrl .next_page').attr('disabled', 'disabled').addClass('btn_dis');
        } else {
            $(obj_box + ' .page_ctrl .next_page').removeAttr('disabled').removeClass('btn_dis');
        }
    }

    page_even();

    $(obj_box + ' .page_ctrl').on('click', 'button', function () {
        var that = $(this);
        if (that.hasClass('prev_page')) {
            if (current_page != 1) {
                current_page--;
                that.parent('.page_ctrl').html('');
                page_even();
            }
        }
        else if (that.hasClass('next_page')) {
            if (current_page != total_page) {
                current_page++;
                that.parent('.page_ctrl').html('');
                page_even();
            }
        }
        else if (that.hasClass('page_num') && !that.hasClass('current_page')) {
            current_page = parseInt(that.html());
            that.parent('.page_ctrl').html('');
            page_even();
        }
        else if (that.hasClass('to_page_num')) {
            current_page = parseInt(that.siblings('.input_page_num').val());
            that.parent('.page_ctrl').html('');
            page_even();
        }
    });
}