(($) ->
    $.fn.tree = () ->
        tree = $(this)
        tree.on('click', '.toggle-children', (e) ->
            e.preventDefault()
            $(this).closest('.tree-row')
                .toggleClass('collapsed')
                .toggleClass('expanded')
        )
        if tree.hasClass('tree-sortable')
            tree.nestedSortable({
                handle: '> .element > .handle',
                items: 'li.tree-row',
                toleranceElement: '> .element',
                startCollapsed: true,
                branchClass: 'branch',
                collapsedClass: 'collapsed',
                isTree: true,
                helper: 'clone',
                expandedClass: 'expanded',
                #errorClass
                #Given to the placeholder in case of error. Default: mjs-nestedSortable-error
                #expandedClass (2.0)
                #Given to branches that are expanded. Default: mjs-nestedSortable-expanded
                hoveringClass: 'sortable-hover',
                leafClass: 'leaf',
                placeholder: 'sortable-placeholder',
                tolerance: 'pointer',
                opacity: 0.7,
                tabSize: 22,
                start: ((e, ui) ->
                    ui.item.show().addClass('sortable-active')
                ),
                stop: ((e, ui) ->
                    ui.item.show().removeClass('sortable-active')
                    ui.item.find('.tree-row').add(ui.item).each(->
                        level = $(this).parents('.tree-row').size()
                        $(this)
                            .removeClass((el, c) -> c.match(/level-\d+/)[0])
                            .addClass("level-#{level + 1}")
                    )
                )
                update: ((e, ui) ->
                    console.log 'sorted'
                    c = ui.item.data('id')
                    p = ui.item.parent().closest('.tree-row').data('id')
                    s = ui.item.prev('.tree-row').data('id')
                    console.log c, p, s
                    url = ui.item.closest('.tree').data('sorting-endpoint')
                    $.ajax({
                        url: url,
                        type: 'post',
                        data: {
                            category: c,
                            parent: p,
                            previous_sibling: s,
                        },
                        success: (data) ->
                            label = $('> .element > .tree-row-label > div', ui.item)
                            el = label.find('.status')
                            if el.size()
                                el.finish()
                            el = $('<span class="status">Successfully moved</span>')
                            label.append(el)
                            el.fadeOut({
                                duration: 3000,
                                complete: -> el.remove()
                            })
                    })
                ),
            })
)(jQuery)
