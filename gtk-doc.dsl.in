<!DOCTYPE style-sheet PUBLIC "-//James Clark//DTD DSSSL Style Sheet//EN" [
<!ENTITY dbstyle PUBLIC "-//Norman Walsh//DOCUMENT DocBook HTML Stylesheet//EN" CDATA DSSSL>
]>

<style-sheet>
<style-specification use="docbook">
<style-specification-body>

(define gtkdoc-version "")
(define gtkdoc-bookname "")

;; These are some customizations to the standard HTML output produced by the
;; Modular DocBook Stylesheets.
;; I've copied parts of a few functions from the stylesheets so these should
;; be checked occasionally to ensure they are up to date.
;;
;; The last check was with version 1.40 of the stylesheets.
;; It will not work with versions < 1.19 since the $shade-verbatim-attr$
;; function was added then. Versions 1.19 to 1.39 may be OK, if you're lucky!

;;(define %generate-book-toc% #f)

;; If a Chapter has role="no-toc" we don't generate a table of contents.
;; This is useful if a better contents page has been added manually, e.g. for
;; the GTK+ Widgets & Objects page. (But it is a bit of a hack.)
(define ($generate-chapter-toc$)
  (not (equal? (attribute-string (normalize "role") (current-node)) "no-toc")))

(define %chapter-autolabel% 
  ;; Are chapters enumerated?
  #f)

(define %use-id-as-filename% #t)

(define %html-ext% ".html")

(define ($user-html-header$ #!optional
                            (home (empty-node-list))
                            (up (empty-node-list))
                            (prev (empty-node-list))
                            (next (empty-node-list)))
  (make sequence
    (if (not (string=? gtkdoc-version ""))
	(make empty-element gi: "META"
	      attributes: (list
			   (list "NAME" "GENERATOR")
			   (list "CONTENT" (string-append
					  "GTK-Doc V"
					  gtkdoc-version
					  " (SGML mode)"))))
	(empty-sosofo))
    (make element gi: "STYLE"
	  attributes: (list (list "TYPE" "text/css"))
	  (literal ".synopsis, .classsynopsis {
    background: #eeeeee;
    border: solid 1px #aaaaaa;
    padding: 0.5em;
}
.programlisting {
    background: #eeeeff;
    border: solid 1px #aaaaff;
    padding: 0.5em;
}
.variablelist {
    padding: 4px;
    margin-left: 3em;
}
.navigation {
    background: #ffeeee;
    border: solid 1px #ffaaaa;
    margin-top: 0.5em;
    margin-bottom: 0.5em;
}
.navigation a {
    color: #770000;
}
.navigation a:visited {
    color: #550000;
}
.navigation .title {
    font-size: 200%;
}"))))


(mode book-titlepage-recto-mode
  (element title 
    (make element gi: "TABLE"
	  attributes: (list
		       (list "CLASS" "navigation")
		       (list "WIDTH" %gentext-nav-tblwidth%)
		       (list "CELLPADDING" "2")
		       (list "CELLSPACING" "0"))
	  (make element gi: "TR"
		(make element gi: "TH"
		      attributes: (list
				   (list "ALIGN" "center")
                                  (list "VALIGN" "MIDDLE"))
		      (make element gi: "P"
			    attributes: (list (list "CLASS" (gi)))
			    (process-children-trim)
			    (make empty-element gi: "A"
				  attributes: (list (list "NAME" (element-id))))))))))

(define (book-titlepage-separator side)
  (empty-sosofo))


;; This overrides the variablelist definition (copied from 1.76,
;; dblists.dsl).  It changes the table background color, cell spacing
;; and cell padding.
;;
;; I have also removed the code to handle the non-table case.
(element variablelist
    (make sequence
      (if %spacing-paras%
          (make element gi: "P" (empty-sosofo))
          (empty-sosofo))
      (para-check)

      (make element gi: "TABLE"
            attributes: '(("CLASS" "variablelist")
			  ("BORDER" "0")
			  ("CELLSPACING" "0")
			  ("CELLPADDING" "4"))
            (if %html40%
                (make element gi: "TBODY"
                      (with-mode variablelist-table
                        (process-children)))
                (with-mode variablelist-table
                  (process-children))))
      (para-check 'restart)))

(mode variablelist-table
  (element (variablelist title)
    (make element gi: "TR"
          attributes: '(("CLASS" "TITLE"))
          (make element gi: "TH"
                attributes: '(("ALIGN" "LEFT")
                              ("VALIGN" "TOP")
                              ("COLSPAN" "2"))
                (process-children))))

  (element varlistentry
    (let* ((terms      (select-elements (children (current-node))
                                        (normalize "term")))
           (listitem   (select-elements (children (current-node))
                                        (normalize "listitem"))))

      (make element gi: "TR"
            (make element gi: "TD"
                  attributes: '(("ALIGN" "LEFT")
                                ("VALIGN" "TOP"))
                  (make empty-element gi: "A"
                        attributes: (list
                                     (list "NAME" (element-id))))
                  (process-node-list terms))
            (make element gi: "TD"
                  attributes: '(("ALIGN" "LEFT")
                                ("VALIGN" "TOP"))
                  (process-node-list listitem)))))
  
  (element (varlistentry term)
    (make sequence
      (if %css-decoration%
          (make element gi: "SPAN"
                attributes: '(("STYLE" "white-space: nowrap"))
                (process-children-trim))
          (make element gi: "NOBR"
                (process-children-trim)))
      (if (not (last-sibling?))
          (literal ", ")
          (literal ""))))

  (element (varlistentry listitem)
    (process-children))
)


;; This overrides the refsect2 definition (copied from 1.20, dbrfntry.dsl).
;; It puts a horizontal rule before each function/struct/... description,
;; except the first one in the refsect1.
(element refsect2
  (make sequence
    (if (first-sibling?)
	(empty-sosofo)
	(make empty-element gi: "HR"))
    ($block-container$)))

;; Override the book declaration, so that we generate a crossreference
;; for the book

(element book 
  (let* ((bookinfo  (select-elements (children (current-node)) (normalize "bookinfo")))
	 (ititle   (select-elements (children bookinfo) (normalize "title")))
	 (title    (if (node-list-empty? ititle)
		       (select-elements (children (current-node)) (normalize "title"))
		       (node-list-first ititle)))
	 (nl       (titlepage-info-elements (current-node) bookinfo))
	 (tsosofo  (with-mode head-title-mode
		     (process-node-list title)))
	 (dedication (select-elements (children (current-node)) (normalize "dedication"))))
    (make sequence
     (html-document 
      tsosofo
      (make element gi: "DIV"
	    attributes: '(("CLASS" "BOOK"))
	    (if %generate-book-titlepage%
		(make sequence
		  (book-titlepage nl 'recto)
		  (book-titlepage nl 'verso))
		(empty-sosofo))
	    
	    (if (node-list-empty? dedication)
		(empty-sosofo)
		(with-mode dedication-page-mode
		  (process-node-list dedication)))
	    
	    (if (not (generate-toc-in-front))
		(process-children)
		(empty-sosofo))
	    
	    (if %generate-book-toc%
		(build-toc (current-node) (toc-depth (current-node)))
		(empty-sosofo))
	    
	    ;;	  (let loop ((gilist %generate-book-lot-list%))
	    ;;	    (if (null? gilist)
	    ;;		(empty-sosofo)
	    ;;		(if (not (node-list-empty? 
	    ;;			  (select-elements (descendants (current-node))
	    ;;					   (car gilist))))
	    ;;		    (make sequence
	    ;;		      (build-lot (current-node) (car gilist))
	    ;;		      (loop (cdr gilist)))
	    ;;		    (loop (cdr gilist)))))
	  
	    (if (generate-toc-in-front)
		(process-children)
		(empty-sosofo))))
     (make entity 
       system-id: "index.sgml"
       (with-mode generate-index-mode
	 (process-children))))))

;; Mode for generating cross references

(define (process-child-elements)
  (process-node-list
   (node-list-map (lambda (snl)
                    (if (equal? (node-property 'class-name snl) 'element)
                        snl
                        (empty-node-list)))
                  (children (current-node)))))

(mode generate-index-mode
  (element anchor
    (if (attribute-string "href" (current-node))
	(empty-sosofo)
	(make formatting-instruction data:
	      (string-append "\less-than-sign;ANCHOR id =\""
			     (attribute-string "id" (current-node))
			     "\" href=\""
			     (if (not (string=? gtkdoc-bookname ""))
				 (string-append gtkdoc-bookname "/")
				 "")
			     (href-to (current-node))
			     "\"\greater-than-sign;
"))))

  ;; We also want to be able to link to complete RefEntry.
  (element refentry
    (make sequence
      (make formatting-instruction data:
	    (string-append "\less-than-sign;ANCHOR id =\""
			   (attribute-string "id" (current-node))
			   "\" href=\""
			   (if (not (string=? gtkdoc-bookname ""))
			       (string-append gtkdoc-bookname "/")
			       "")
			   (href-to (current-node))
			   "\"\greater-than-sign;
"))
      (process-child-elements)))

  (default
    (process-child-elements)))

;; For hypertext links for which no target is found in the document, we output
;; our own special tag which we use later to resolve cross-document links.
(element link 
  (let* ((target (element-with-id (attribute-string (normalize "linkend")))))
    (if (node-list-empty? target)
      (make element gi: "GTKDOCLINK"
	    attributes: (list
			 (list "HREF" (attribute-string (normalize "linkend"))))
            (process-children))
      (make element gi: "A"
            attributes: (list
                         (list "HREF" (href-to target)))
            (process-children)))))


;; This overrides default-header-nav-tbl-noff (copied from 1.20, dbnavig.dsl).
;; I want 'Home' and 'Up' links at the top of each page, and white text on
;; black.
(define (default-header-nav-tbl-noff elemnode prev next prevsib nextsib)
  (let* ((up (parent elemnode))
	 (home (nav-home elemnode))
	 (show-title? (nav-banner? elemnode))
	 (title-sosofo
	      (make element gi: "TH"
		    attributes: (list
				 (list "WIDTH" "100%")
				 (list "align" "center"))
		    (if show-title?
			(nav-banner elemnode)
			(empty-sosofo))))
	 (show-banner? (or show-title?
			   (not (node-list-empty? prev))
			   (not (node-list-empty? next))
			   (nav-context? elemnode)))
	 (banner-sosofo
	      (make element gi: "TR"
		    attributes: (list
				 (list "VALIGN" "middle"))
		    (if (not (node-list-empty? prev))
			(make element gi: "TD"
			      (make element gi: "A"
				    attributes: (list
						 (list "ACCESSKEY" "p")
						 (list "HREF"
						       (href-to prev)))
				    (make empty-element gi: "IMG"
					  attributes: (list
						       (list "SRC" "left.png")
						       (list "WIDTH" "24")
						       (list "HEIGHT" "24")
						       (list "BORDER" "0")
						       (list "ALT" "Prev")))))
			(empty-sosofo))
		    (if (nav-up? elemnode)
			(make element gi: "TD"
			      (make element gi: "A"
				    attributes: (list
						 (list "ACCESSKEY" "u")
						 (list "HREF"
						       (href-to up)))
				    (make empty-element gi: "IMG"
					  attributes: (list
						       (list "SRC" "up.png")
						       (list "WIDTH" "24")
						       (list "HEIGHT" "24")
						       (list "BORDER" "0")
						       (list "ALT" "Up")))))
			(empty-sosofo))
		    (if (nav-home? elemnode)
			(make element gi: "TD"
			      (make element gi: "A"
				    attributes: (list
						 (list "ACCESSKEY" "h")
						 (list "HREF"
						       (href-to home)))
				    (make empty-element gi: "IMG"
					  attributes: (list
						       (list "SRC" "home.png")
						       (list "WIDTH" "24")
						       (list "HEIGHT" "24")
						       (list "BORDER" "0")
						       (list "ALT" "Home")))))
			(empty-sosofo))
		    title-sosofo
		    (if (not (node-list-empty? next))
			(make element gi: "TD"
			      (make element gi: "A"
				    attributes: (list
						 (list "ACCESSKEY" "n")
						 (list "HREF"
						       (href-to next)))
				    (make empty-element gi: "IMG"
					  attributes: (list
						       (list "SRC" "right.png")
						       (list "WIDTH" "24")
						       (list "HEIGHT" "24")
						       (list "BORDER" "0")
						       (list "ALT" "Next")))))
			(empty-sosofo)))))
	 
    (if show-banner?
	(make element gi: "TABLE"
	      attributes: (list
			   (list "WIDTH" %gentext-nav-tblwidth%)
			   (list "CLASS" "navigation")
			   (list "SUMMARY" "Navigation header")
			   (list "CELLPADDING" "2")
			   (list "CELLSPACING" "2"))
	      banner-sosofo)
	(empty-sosofo))))

;; This overrides default-footer-nav-tbl (copied from 1.20, dbnavig.dsl).
;; It matches the header above.
(define (default-footer-nav-tbl elemnode prev next prevsib nextsib)
  (let* ((show-footer? (or (not (node-list-empty? prev))
			  (not (node-list-empty? next))))
	 (footer-sosofo
	     (make element gi: "TR"
		   attributes: (list
				(list "VALIGN" "middle"))
		   (make element gi: "TD"
			 attributes: (list
				      (list "ALIGN" "left"))
			 (if (not (node-list-empty? prev))
			     (make element gi: "A"
				   attributes: (list
						(list "ACCESSKEY" "p")
						(list "HREF" (href-to prev)))
				   (make element gi: "B"
					 (make entity-ref name: "lt")
					 (make entity-ref name: "lt")
					 (make entity-ref name: "lt")
					 (make entity-ref name: "nbsp")
					 (element-title-sosofo prev)))
			     (empty-sosofo)))
		   (make element gi: "TD"
			 attributes: (list
				      (list "ALIGN" "right"))
			 (if (not (node-list-empty? next))
			     (make element gi: "A"
				   attributes: (list
						(list "ACCESSKEY" "n")
						(list "HREF" (href-to next)))
				   (make element gi: "B"
					 (element-title-sosofo next)
					 (make entity-ref name: "nbsp")
					 (make entity-ref name: "gt")
					 (make entity-ref name: "gt")
					 (make entity-ref name: "gt")))
			     (empty-sosofo))))))
  
    (if show-footer?
	(make element gi: "TABLE"
	      attributes: (list
			   (list "CLASS" "navigation")
			   (list "WIDTH" %gentext-nav-tblwidth%)
			   (list "SUMMARY" "Navigation footer")
			   (list "CELLPADDING" "2")
			   (list "CELLSPACING" "2"))
	      footer-sosofo)
	(empty-sosofo))))


(define ($section-body$)
  (make sequence
    (make empty-element gi: "BR"
	  attributes: (list (list "CLEAR" "all")))
    (make element gi: "DIV"
	  attributes: (list (list "CLASS" (gi)))
	  ($section-separator$)
	  ($section-title$)
	  (process-children))))

</style-specification-body>
</style-specification>
<external-specification id="docbook" document="dbstyle">
</style-sheet>
